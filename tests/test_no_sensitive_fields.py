"""SEC-006 / Test Plan 5.1 Confidentiality: no API response ever contains a password hash,
the raw password or the token signing secret."""
import pytest
from django.conf import settings

PASSWORD = "Passw0rd!"


def walk_keys(data):
    """Every key name anywhere inside a JSON value."""
    if isinstance(data, dict):
        for key, value in data.items():
            yield key
            yield from walk_keys(value)
    elif isinstance(data, list):
        for item in data:
            yield from walk_keys(item)


def assert_safe(response):
    body = response.content.decode()
    assert "pbkdf2_" not in body, "password hash leaked"
    assert PASSWORD not in body, "raw password leaked"
    assert settings.SECRET_KEY not in body, "signing secret leaked"
    if response.get("Content-Type", "").startswith("application/json"):
        assert "password" not in set(walk_keys(response.json())), "password field returned"


@pytest.mark.django_db
def test_no_endpoint_leaks_secrets(api):
    responses = []
    responses.append(api.post("/api/v1/auth/register/", {"email": "a@test.com", "password": PASSWORD}, format="json"))
    login = api.post("/api/v1/auth/login/", {"email": "a@test.com", "password": PASSWORD}, format="json")
    responses.append(login)
    responses.append(api.post("/api/v1/auth/login/", {"email": "a@test.com", "password": "WrongPass1"}, format="json"))
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['token']}")

    category = api.post("/api/v1/categories/", {"name": "Food"}, format="json")
    responses.append(category)
    cat_id = category.json()["id"]
    expense = api.post(
        "/api/v1/expenses/", {"category": cat_id, "amount": "250.00", "expense_date": "2026-01-15"}, format="json"
    )
    responses.append(expense)
    budget = api.post(
        "/api/v1/budgets/",
        {"category": cat_id, "period": "MONTHLY", "limit_amount": "1000.00", "start_date": "2026-01-01"},
        format="json",
    )
    responses.append(budget)

    for path in [
        "/api/v1/auth/me/",
        "/api/v1/expenses/",
        f"/api/v1/expenses/{expense.json()['id']}/",
        "/api/v1/categories/",
        "/api/v1/budgets/",
        f"/api/v1/budgets/{budget.json()['id']}/",
        "/api/v1/analytics/?from=2026-01-01&to=2026-01-31",
    ]:
        responses.append(api.get(path))

    for response in responses:
        assert response.status_code < 500
        assert_safe(response)


@pytest.mark.django_db
def test_error_responses_do_not_leak(api):
    api.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
    assert_safe(api.get("/api/v1/expenses/"))
    api.credentials()
    assert_safe(api.post("/api/v1/auth/register/", {"email": "bad", "password": PASSWORD}, format="json"))
