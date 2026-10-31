
"""FR-010: users can update or delete only the budgets they own."""
import pytest

from accounts.models import User
from budgets.models import Budget


@pytest.fixture
def budget(user, category):
    return Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="1000.00",
        start_date="2026-01-01",
    )


def url(budget):
    return f"/api/v1/budgets/{budget.id}/"


@pytest.mark.django_db
def test_owner_can_change_limit(api, user, budget):
    api.force_authenticate(user=user)
    response = api.patch(
        url(budget),
        {"limit_amount": "1500.00"},
        format="json",
    )
    assert response.status_code == 200
    budget.refresh_from_db()
    assert str(budget.limit_amount) == "1500.00"


@pytest.mark.django_db
def test_editing_does_not_clash_with_itself(api, user, budget):
    api.force_authenticate(user=user)
    response = api.patch(
        url(budget),
        {"start_date": "2026-01-05"},
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_into_another_budgets_period_gives_409(
    api, user, category, budget
):
    later = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="500.00",
        start_date="2026-02-01",
    )
    api.force_authenticate(user=user)
    response = api.patch(
        url(later),
        {"start_date": "2026-01-20"},
        format="json",
    )
    assert response.status_code == 409


@pytest.mark.django_db
def test_edit_rejects_zero_limit(api, user, budget):
    api.force_authenticate(user=user)
    response = api.patch(
        url(budget),
        {"limit_amount": "0"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_owner_can_delete_budget(api, user, budget):
    api.force_authenticate(user=user)
    response = api.delete(url(budget))
    assert response.status_code == 204
    assert not Budget.objects.filter(id=budget.id).exists()


@pytest.mark.django_db
def test_other_user_cannot_edit_or_delete(api, budget):
    stranger = User.objects.create_user(
        username="b@test.com",
        email="b@test.com",
        password="Passw0rd!",
    )
    api.force_authenticate(user=stranger)

    assert api.patch(
        url(budget),
        {"limit_amount": "1"},
        format="json",
    ).status_code == 403

    assert api.delete(url(budget)).status_code == 403


@pytest.mark.django_db
def test_list_shows_only_own_budgets(api, user, category, budget):
    stranger = User.objects.create_user(
        username="b@test.com",
        email="b@test.com",
        password="Passw0rd!",
    )
    Budget.objects.create(
        user=stranger,
        category=category,
        period="MONTHLY",
        limit_amount="9",
        start_date="2026-01-01",
    )

    api.force_authenticate(user=user)
    rows = api.get("/api/v1/budgets/").json()

    assert [row["id"] for row in rows] == [str(budget.id)]
