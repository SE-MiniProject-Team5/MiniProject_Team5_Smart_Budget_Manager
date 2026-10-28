"""FR-005, FR-008 and SRS 6.5 business rules: adding expenses."""
import pytest

from accounts.models import User
from expenses.models import Category, Expense

URL = "/api/v1/expenses/"


def payload(category, **overrides):
    data = {"category": str(category.id), "amount": "250.00", "expense_date": "2026-01-15", "note": "lunch"}
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_add_valid_expense_returns_201(api, user, category):  # TC-FUN-03
    api.force_authenticate(user=user)
    response = api.post(URL, payload(category), format="json")
    assert response.status_code == 201
    expense = Expense.objects.get()
    assert expense.user == user
    assert str(expense.amount) == "250.00"


@pytest.mark.django_db
@pytest.mark.parametrize("amount", ["0", "-5"])
def test_zero_or_negative_amount_rejected(api, user, category, amount):  # TC-FUN-04, FR-008
    api.force_authenticate(user=user)
    response = api.post(URL, payload(category, amount=amount), format="json")
    assert response.status_code == 400
    assert "amount" in response.json()
    assert Expense.objects.count() == 0


@pytest.mark.django_db
def test_note_longer_than_255_rejected(api, user, category):  # FR-005
    api.force_authenticate(user=user)
    response = api.post(URL, payload(category, note="x" * 256), format="json")
    assert response.status_code == 400
    assert "note" in response.json()


@pytest.mark.django_db
def test_inactive_category_rejected(api, user):  # SRS 6.5
    api.force_authenticate(user=user)
    old = Category.objects.create(name="Old", is_active=False)
    response = api.post(URL, payload(old), format="json")
    assert response.status_code == 400
    assert "category" in response.json()


@pytest.mark.django_db
def test_other_users_custom_category_rejected(api, user):
    other = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    theirs = Category.objects.create(name="Theirs", owner=other)
    api.force_authenticate(user=user)
    response = api.post(URL, payload(theirs), format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_own_custom_category_allowed(api, user):
    mine = Category.objects.create(name="Mine", owner=user)
    api.force_authenticate(user=user)
    assert api.post(URL, payload(mine), format="json").status_code == 201


@pytest.mark.django_db
def test_owner_in_json_is_ignored(api, user, category):
    other = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    api.force_authenticate(user=user)
    api.post(URL, payload(category, user=str(other.id)), format="json")
    assert Expense.objects.get().user == user


@pytest.mark.django_db
def test_list_shows_only_own_expenses(api, user, category):
    other = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    Expense.objects.create(user=other, category=category, amount="10", expense_date="2026-01-15")
    Expense.objects.create(user=user, category=category, amount="20", expense_date="2026-01-15")
    api.force_authenticate(user=user)
    rows = api.get(URL).json()
    assert len(rows) == 1
    assert rows[0]["amount"] == "20.00"


@pytest.mark.django_db
def test_anonymous_caller_refused(api, category):
    response = api.post(URL, payload(category), format="json")
    assert response.status_code in (401, 403)