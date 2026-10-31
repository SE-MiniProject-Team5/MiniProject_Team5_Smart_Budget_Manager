"""FR-006: users can edit or delete only the expenses they own."""
import pytest

from accounts.models import User
from expenses.models import Expense


@pytest.fixture
def expense(user, category):
    return Expense.objects.create(user=user, category=category, amount="100.00", expense_date="2026-01-15")


@pytest.fixture
def stranger(db):
    return User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")


def url(expense):
    return f"/api/v1/expenses/{expense.id}/"


@pytest.mark.django_db
def test_owner_can_edit_expense(api, user, category, expense):
    api.force_authenticate(user=user)
    data = {"category": str(category.id), "amount": "120.50", "expense_date": "2026-01-16", "note": "fixed"}
    response = api.put(url(expense), data, format="json")
    assert response.status_code == 200
    expense.refresh_from_db()
    assert str(expense.amount) == "120.50"
    assert expense.note == "fixed"


@pytest.mark.django_db
def test_owner_can_change_one_field(api, user, expense):
    api.force_authenticate(user=user)
    response = api.patch(url(expense), {"note": "only the note"}, format="json")
    assert response.status_code == 200
    expense.refresh_from_db()
    assert expense.note == "only the note"


@pytest.mark.django_db
def test_edit_still_rejects_zero_amount(api, user, expense):  # FR-008 also applies to edits
    api.force_authenticate(user=user)
    response = api.patch(url(expense), {"amount": "0"}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_owner_can_delete_expense(api, user, expense):
    api.force_authenticate(user=user)
    assert api.delete(url(expense)).status_code == 204
    assert not Expense.objects.filter(id=expense.id).exists()


@pytest.mark.django_db
def test_other_user_cannot_edit_or_delete(api, stranger, expense):  # Test Plan 5.1 Confidentiality
    api.force_authenticate(user=stranger)
    assert api.patch(url(expense), {"note": "hacked"}, format="json").status_code == 403
    assert api.delete(url(expense)).status_code == 403
    expense.refresh_from_db()
    assert expense.note == ""


@pytest.mark.django_db
def test_unknown_id_gives_404(api, user):
    api.force_authenticate(user=user)
    response = api.get("/api/v1/expenses/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404