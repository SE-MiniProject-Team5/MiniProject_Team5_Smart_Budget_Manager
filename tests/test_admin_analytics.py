"""FR-020: administrators see anonymised usage totals; FR-021: others get 403."""
import pytest

from accounts.models import User
from expenses.models import Category, Expense

URL = "/api/v1/admin/analytics/"


@pytest.mark.django_db
def test_admin_sees_totals_only(api, user, category):
    admin = User.objects.create_user(
        username="admin@test.com", email="admin@test.com", password="Passw0rd!", role=User.Role.ADMIN
    )
    Category.objects.create(name="Unused")
    Expense.objects.create(user=user, category=category, amount="10.00", expense_date="2026-01-10")
    Expense.objects.create(user=user, category=category, amount="20.00", expense_date="2026-01-11")
    api.force_authenticate(user=admin)
    response = api.get(URL)
    assert response.status_code == 200
    assert response.json() == {
        "total_users": 2,
        "active_users": 2,
        "total_expenses": 2,
        "categories_in_use": 1,
        "active_predefined_categories": 2,
    }
    assert "u1@test.com" not in response.content.decode()  # no personal data


@pytest.mark.django_db
def test_regular_user_gets_403(api, user):  # FR-021
    api.force_authenticate(user=user)
    assert api.get(URL).status_code == 403


@pytest.mark.django_db
def test_anonymous_gets_401(api):
    assert api.get(URL).status_code == 401
