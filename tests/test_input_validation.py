"""SEC-003: all user input is validated and sanitised on the server, whatever the client sends."""
import pytest

from expenses.models import Category, Expense

EXPENSES = "/api/v1/expenses/"
CATEGORIES = "/api/v1/categories/"


def expense(cat, **overrides):
    data = {"category": str(cat.id), "amount": "100.00", "expense_date": "2026-01-15", "note": "lunch"}
    data.update(overrides)
    return data


@pytest.mark.django_db
@pytest.mark.parametrize("note", ["<script>alert(1)</script>", "<b>bold</b>", "a > b"])
def test_html_in_note_rejected(api, user, category, note):
    api.force_authenticate(user=user)
    response = api.post(EXPENSES, expense(category, note=note), format="json")
    assert response.status_code == 400
    assert "note" in response.json()
    assert Expense.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("note", ["line1\nline2", "tab\there", "null\x00byte"])
def test_control_characters_in_note_rejected(api, user, category, note):
    api.force_authenticate(user=user)
    assert api.post(EXPENSES, expense(category, note=note), format="json").status_code == 400


@pytest.mark.django_db
def test_note_is_trimmed(api, user, category):
    api.force_authenticate(user=user)
    response = api.post(EXPENSES, expense(category, note="   coffee   "), format="json")
    assert response.status_code == 201
    assert Expense.objects.get().note == "coffee"


@pytest.mark.django_db
def test_html_in_category_name_rejected(api, user):
    api.force_authenticate(user=user)
    response = api.post(CATEGORIES, {"name": "<img src=x>"}, format="json")
    assert response.status_code == 400
    assert not Category.objects.filter(owner=user).exists()


@pytest.mark.django_db
def test_html_rejected_on_edit_too(api, user, category):
    api.force_authenticate(user=user)
    created = api.post(EXPENSES, expense(category), format="json").json()
    response = api.patch(f"{EXPENSES}{created['id']}/", {"note": "<script>"}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": "abc"},
        {"amount": "12345678901"},  # more digits than the field allows
        {"amount": "10.999"},  # more than 2 decimal places
        {"expense_date": "31-01-2026"},
        {"expense_date": "2026-02-30"},
        {"category": "not-a-uuid"},
        {"category": "00000000-0000-0000-0000-000000000000"},
    ],
)
def test_malformed_values_rejected(api, user, category, overrides):
    api.force_authenticate(user=user)
    assert api.post(EXPENSES, expense(category, **overrides), format="json").status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize("missing", ["category", "amount", "expense_date"])
def test_missing_required_field_rejected(api, user, category, missing):
    api.force_authenticate(user=user)
    data = expense(category)
    del data[missing]
    response = api.post(EXPENSES, data, format="json")
    assert response.status_code == 400
    assert missing in response.json()


@pytest.mark.django_db
def test_body_that_is_not_json_object_rejected(api, user):
    api.force_authenticate(user=user)
    response = api.post(EXPENSES, "[1, 2, 3]", content_type="application/json")
    assert response.status_code == 400
