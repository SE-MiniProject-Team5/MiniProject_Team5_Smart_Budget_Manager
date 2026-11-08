"""TEST-M2: unit tests for the expenses module, part 2: rules enforced through
the API (FR-005 to FR-008, SEC-003)."""
import pytest

from expenses.models import Expense


@pytest.fixture
def client(api, user):
    api.force_authenticate(user=user)
    return api


@pytest.mark.django_db
def test_category_name_of_only_spaces_is_refused(client):
    response = client.post("/api/v1/categories/", {"name": "    "}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_category_name_over_50_characters_is_refused(client):
    response = client.post("/api/v1/categories/", {"name": "x" * 51}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_zero_amount_is_refused(client, category):
    body = {"category": str(category.id), "amount": "0.00", "expense_date": "2026-01-05"}
    assert client.post("/api/v1/expenses/", body, format="json").status_code == 400


@pytest.mark.django_db
def test_negative_amount_is_refused(client, category):
    body = {"category": str(category.id), "amount": "-5.00", "expense_date": "2026-01-05"}
    assert client.post("/api/v1/expenses/", body, format="json").status_code == 400


@pytest.mark.django_db
def test_note_is_saved_trimmed(client, category):
    body = {"category": str(category.id), "amount": "5.00", "expense_date": "2026-01-05", "note": "  bus  "}
    response = client.post("/api/v1/expenses/", body, format="json")
    assert response.status_code == 201
    assert Expense.objects.get().note == "bus"


@pytest.mark.django_db
def test_a_user_sees_only_their_own_expenses(client, user, category):
    from accounts.models import User

    other = User.objects.create_user(username="o@test.com", email="o@test.com", password="Passw0rd!")
    Expense.objects.create(user=other, category=category, amount="9.00", expense_date="2026-01-05")
    Expense.objects.create(user=user, category=category, amount="1.00", expense_date="2026-01-05")
    response = client.get("/api/v1/expenses/")
    body = response.json()
    rows = body["results"] if isinstance(body, dict) else body
    assert [row["amount"] for row in rows] == ["1.00"]
