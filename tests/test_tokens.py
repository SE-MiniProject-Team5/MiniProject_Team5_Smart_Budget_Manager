"""SEC-004: protected endpoints accept a valid token and reject bad or
expired ones with 401."""
import logging
import pytest
from accounts import tokens
PROTECTED = "/api/v1/expenses/"
def login(api):
    response = api.post("/api/v1/auth/login/", {"email": "u1@test.com",
    "password": "Passw0rd!"}, format="json")
    return response.json()["token"]
@pytest.mark.django_db
def test_valid_token_is_accepted(api, user):
    token = login(api)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert api.get(PROTECTED).status_code == 200
@pytest.mark.django_db
def test_no_token_gives_401(api):
    assert api.get(PROTECTED).status_code == 401
@pytest.mark.django_db
def test_malformed_token_gives_401_and_is_logged(api, caplog): # TC-SEC-03
    api.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
    with caplog.at_level(logging.INFO, logger="security"):
        response = api.get(PROTECTED)
    assert response.status_code == 401
    assert "event=invalid_token" in caplog.text
@pytest.mark.django_db
def test_expired_token_gives_401(api, user, monkeypatch): # TC-SEC-03
    token = login(api)
    monkeypatch.setattr(tokens, "MAX_AGE_SECONDS", -1) # pretend more than 24 hours have passed
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert api.get(PROTECTED).status_code == 401
@pytest.mark.django_db
def test_token_of_deleted_user_gives_401(api, user):
    token = login(api)
    user.delete()
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert api.get(PROTECTED).status_code == 401
