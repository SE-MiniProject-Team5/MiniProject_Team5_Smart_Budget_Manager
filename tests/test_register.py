"""FR-001, FR-002, SEC-001: user registration."""
import pytest
from accounts.models import User
URL = "/api/v1/auth/register/"
@pytest.mark.django_db
def test_register_success_returns_201_and_creates_user(api): # TC-FUN-01
    response = api.post(URL, {"email": "a@test.com", "password":
    "Passw0rd!"}, format="json")
    assert response.status_code == 201
    assert response.json()["email"] == "a@test.com"
    assert User.objects.filter(email="a@test.com").exists()
@pytest.mark.django_db
def test_password_is_stored_hashed(api): # TC-SEC-01, SEC-001
    api.post(URL, {"email": "a@test.com", "password": "Passw0rd!"},
    format="json")
    user = User.objects.get(email="a@test.com")
    assert user.password != "Passw0rd!"
    assert user.check_password("Passw0rd!")
@pytest.mark.django_db
def test_short_password_rejected_with_400(api): # FR-001
    response = api.post(URL, {"email": "a@test.com", "password": "short"},
    format="json")
    assert response.status_code == 400
    assert "password" in response.json()

@pytest.mark.django_db
def test_invalid_email_rejected_with_400(api):
    response = api.post(URL, {"email": "not-an-email", "password":
    "Passw0rd!"}, format="json")
    assert response.status_code == 400
    assert "email" in response.json()
@pytest.mark.django_db
def test_duplicate_email_rejected_with_409_ignoring_case(api): # FR-002
    api.post(URL, {"email": "a@test.com", "password": "Passw0rd!"},
    format="json")
    response = api.post(URL, {"email": "A@Test.com", "password":
    "Passw0rd!"}, format="json")
    assert response.status_code == 409
    assert User.objects.count() == 1
@pytest.mark.django_db
def test_response_never_contains_password(api): # SEC-006
    response = api.post(URL, {"email": "a@test.com", "password":
    "Passw0rd!"}, format="json")
    body = response.content.decode()
    assert "password" not in response.json()
    assert "Passw0rd!" not in body
    assert "pbkdf2" not in body