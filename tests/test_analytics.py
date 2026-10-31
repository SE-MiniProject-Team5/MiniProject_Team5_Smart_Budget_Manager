"""FR-016: spend broken down by category for a chosen date range."""

import pytest

from accounts.models import User
from expenses.models import Category, Expense


URL = "/api/v1/analytics/"


@pytest.fixture
def travel(db):
    return Category.objects.create(name="Travel")


@pytest.mark.django_db
def test_breakdown_groups_totals_by_category(api, user, category, travel):
    # TC-FUN-07
    Expense.objects.create(
        user=user,
        category=category,
        amount="100.00",
        expense_date="2026-01-05",
    )
    Expense.objects.create(
        user=user,
        category=category,
        amount="50.50",
        expense_date="2026-01-20",
    )
    Expense.objects.create(
        user=user,
        category=travel,
        amount="300.00",
        expense_date="2026-01-10",
    )

    api.force_authenticate(user=user)
    response = api.get(
        URL, {"from": "2026-01-01", "to": "2026-01-31"}
    )

    assert response.status_code == 200
    body = response.json()

    assert body["total"] == "450.50"
    assert [
        (row["category"], row["total"])
        for row in body["categories"]
    ] == [("Travel", "300.00"), ("Food", "150.50")]


@pytest.mark.django_db
def test_dates_outside_range_are_ignored(api, user, category):
    Expense.objects.create(
        user=user,
        category=category,
        amount="10.00",
        expense_date="2026-01-31",
    )
    Expense.objects.create(
        user=user,
        category=category,
        amount="99.00",
        expense_date="2026-02-01",
    )

    api.force_authenticate(user=user)
    body = api.get(
        URL, {"from": "2026-01-01", "to": "2026-01-31"}
    ).json()

    assert body["total"] == "10.00"


@pytest.mark.django_db
def test_other_users_expenses_are_not_counted(api, user, category):
    stranger = User.objects.create_user(
        username="b@test.com",
        email="b@test.com",
        password="Passw0rd!",
    )
    Expense.objects.create(
        user=stranger,
        category=category,
        amount="500.00",
        expense_date="2026-01-05",
    )

    api.force_authenticate(user=user)
    body = api.get(
        URL, {"from": "2026-01-01", "to": "2026-01-31"}
    ).json()

    assert body["total"] == "0.00"
    assert body["categories"] == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {},
        {"from": "2026-01-01"},
        {"from": "bad", "to": "2026-01-31"},
        {"from": "2026-02-01", "to": "2026-01-01"},
    ],
)
def test_bad_dates_give_400(api, user, params):
    api.force_authenticate(user=user)

    assert api.get(URL, params).status_code == 400


@pytest.mark.django_db
def test_anonymous_caller_refused(api):
    response = api.get(
        URL, {"from": "2026-01-01", "to": "2026-01-31"}
    )

    assert response.status_code in (401, 403)