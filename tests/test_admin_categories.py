"""FR-019: administrators add, edit and disable master categories; FR-021: others get 403."""
import pytest

from accounts.models import User
from expenses.models import Category, Expense

URL = "/api/v1/admin/categories/"


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="admin@test.com", email="admin@test.com", password="Passw0rd!", role=User.Role.ADMIN
    )


@pytest.mark.django_db
def test_admin_lists_all_master_categories(api, admin, user, category):
    Category.objects.create(name="Retired", is_active=False)
    Category.objects.create(name="Users own", owner=user)
    api.force_authenticate(user=admin)
    names = [row["name"] for row in api.get(URL).json()]
    assert names == ["Food", "Retired"]


@pytest.mark.django_db
def test_admin_adds_master_category(api, admin):
    api.force_authenticate(user=admin)
    response = api.post(URL, {"name": "Health"}, format="json")
    assert response.status_code == 201
    created = Category.objects.get(name="Health")
    assert created.owner is None and created.is_active


@pytest.mark.django_db
def test_admin_renames_category(api, admin, category):
    api.force_authenticate(user=admin)
    assert api.patch(f"{URL}{category.id}/", {"name": "Groceries"}, format="json").status_code == 200
    category.refresh_from_db()
    assert category.name == "Groceries"


@pytest.mark.django_db
def test_disabling_keeps_existing_expenses(api, admin, user, category):  # TC-FUN-08
    expense = Expense.objects.create(user=user, category=category, amount="10.00", expense_date="2026-01-10")
    api.force_authenticate(user=admin)
    response = api.patch(f"{URL}{category.id}/", {"is_active": False}, format="json")
    assert response.status_code == 200
    category.refresh_from_db()
    assert category.is_active is False
    assert Expense.objects.filter(id=expense.id, category=category).exists()


@pytest.mark.django_db
def test_admin_cannot_delete_category(api, admin, category):
    api.force_authenticate(user=admin)
    assert api.delete(f"{URL}{category.id}/").status_code == 405


@pytest.mark.django_db
def test_users_own_category_is_not_managed_here(api, admin, user):
    own = Category.objects.create(name="Mine", owner=user)
    api.force_authenticate(user=admin)
    assert api.patch(f"{URL}{own.id}/", {"is_active": False}, format="json").status_code == 404


@pytest.mark.django_db
def test_blank_or_html_name_rejected(api, admin):
    api.force_authenticate(user=admin)
    assert api.post(URL, {"name": "  "}, format="json").status_code == 400
    assert api.post(URL, {"name": "<b>x</b>"}, format="json").status_code == 400


@pytest.mark.django_db
def test_regular_user_gets_403(api, user, category):  # TC-SEC-02, FR-021
    api.force_authenticate(user=user)
    assert api.post(URL, {"name": "Hack"}, format="json").status_code == 403
    assert api.patch(f"{URL}{category.id}/", {"is_active": False}, format="json").status_code == 403
    category.refresh_from_db()
    assert category.is_active is True
