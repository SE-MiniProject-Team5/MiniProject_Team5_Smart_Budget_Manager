"""TEST-M1: unit tests for the auth module (accounts app), part 2: login tokens,
the Bearer header parser and the User model."""
import pytest
from django.core import signing

from accounts import tokens


# ---- tokens (FR-004, SEC-004) ----

@pytest.mark.django_db
def test_token_round_trip_gives_back_the_user_id(user):
    assert tokens.read_token(tokens.issue_token(user)) == str(user.pk)


@pytest.mark.django_db
def test_tampered_token_is_refused(user):
    token = tokens.issue_token(user)
    with pytest.raises(signing.BadSignature):
        tokens.read_token(token + "tampered")


@pytest.mark.django_db
def test_token_older_than_the_limit_is_refused(user, monkeypatch):
    token = tokens.issue_token(user)
    monkeypatch.setattr(tokens, "MAX_AGE_SECONDS", -1)  # pretend 24 hours have passed
    with pytest.raises(signing.SignatureExpired):
        tokens.read_token(token)


def test_token_lifetime_is_24_hours():
    assert tokens.MAX_AGE_SECONDS == 24 * 60 * 60


# ---- model and header parser ----

@pytest.mark.django_db
def test_user_is_shown_by_email(user):
    assert str(user) == "u1@test.com"


@pytest.mark.django_db
def test_bearer_header_with_extra_parts_gives_401(api):
    api.credentials(HTTP_AUTHORIZATION="Bearer one two")
    assert api.get("/api/v1/expenses/").status_code == 401


@pytest.mark.django_db
def test_other_auth_schemes_are_ignored_and_give_401(api):
    api.credentials(HTTP_AUTHORIZATION="Basic abc123")
    assert api.get("/api/v1/expenses/").status_code == 401
