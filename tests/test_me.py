"""SEC-006: the profile endpoint returns only id, email and role."""
import pytest

URL = "/api/v1/auth/me/"


@pytest.mark.django_db
def test_me_returns_only_safe_fields(api, user):
    api.force_authenticate(user=user)
    response = api.get(URL)
    assert response.status_code == 200
    assert response.json() == {"id": str(user.id), "email": "u1@test.com", "role": "USER"}


@pytest.mark.django_db
def test_me_needs_login(api):
    assert api.get(URL).status_code == 401


@pytest.mark.django_db
def test_register_response_has_only_safe_fields(api):
    response = api.post("/api/v1/auth/register/", {"email": "new@test.com", "password": "Passw0rd!"}, format="json")
    assert response.status_code == 201
    assert set(response.json()) == {"id", "email", "role"}
