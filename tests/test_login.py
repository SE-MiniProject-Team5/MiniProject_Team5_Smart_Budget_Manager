"""FR-003, FR-004: login returns a token valid for at most 24 hours."""
import logging
import pytest
from accounts.tokens import MAX_AGE_SECONDS, read_token
URL = "/api/v1/auth/login/"
@pytest.mark.django_db
def test_login_with_valid_credentials_returns_token(api, user): # TC-FUN-02
    response = api.post(URL, {"email": "u1@test.com", "password":
    "Passw0rd!"}, format="json")
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert read_token(body["token"]) == str(user.id)
@pytest.mark.django_db
def test_token_lifetime_is_at_most_24_hours(api, user): # FR-004
    response = api.post(URL, {"email": "u1@test.com", "password":
    "Passw0rd!"}, format="json")
    assert response.json()["expires_in"] == MAX_AGE_SECONDS <= 24 * 60 * 60
@pytest.mark.django_db
def test_login_email_ignores_capital_letters(api, user):
    response = api.post(URL, {"email": "U1@Test.com", "password":
    "Passw0rd!"}, format="json")
    assert response.status_code == 200
@pytest.mark.django_db
def test_wrong_password_gives_401_and_is_logged(api, user, caplog): # SEC005
    with caplog.at_level(logging.INFO, logger="security"):
        response = api.post(URL, {"email": "u1@test.com", "password":
    "WrongPass1"}, format="json")
    assert response.status_code == 401
    assert "token" not in response.json()
    assert "event=failed_login account=u1@test.com endpoint=/api/v1/auth/login/" in caplog.text
    assert "WrongPass1" not in caplog.text
@pytest.mark.django_db
def test_unknown_email_gives_401(api):
    response = api.post(URL, {"email": "nobody@test.com", "password":
    "Passw0rd!"}, format="json")
    assert response.status_code == 401
@pytest.mark.django_db
def test_missing_password_gives_400(api):
    response = api.post(URL, {"email": "u1@test.com"}, format="json")
    assert response.status_code == 400