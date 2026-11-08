"""TEST-M1: unit tests for the auth module (accounts app), part 1: registration and login checks.

These call the auth functions directly instead of going through the API, so each
rule is checked on its own: password hashing, duplicate emails and login checks.
"""
from unittest import mock

import pytest
from django.db import IntegrityError

from accounts import services
from accounts.models import User


# ---- services.register_user (FR-001, FR-002, SEC-001) ----

@pytest.mark.django_db
def test_register_stores_a_hash_not_the_password():
    user = services.register_user("new@test.com", "Passw0rd!")
    assert user.password != "Passw0rd!"
    assert user.check_password("Passw0rd!")
    assert user.role == User.Role.USER


@pytest.mark.django_db
def test_register_rejects_same_email_in_other_case(user):
    with pytest.raises(services.DuplicateEmailError):
        services.register_user("U1@TEST.COM", "Passw0rd!")


@pytest.mark.django_db
def test_register_race_on_same_email_is_still_a_duplicate():
    # Two requests check at the same moment, both see "no such email", and the
    # database refuses the second insert. That must still count as a duplicate.
    with mock.patch.object(User.objects, "create_user", side_effect=IntegrityError):
        with pytest.raises(services.DuplicateEmailError):
            services.register_user("race@test.com", "Passw0rd!")


# ---- services.authenticate_user (FR-003) ----

@pytest.mark.django_db
def test_login_check_accepts_right_password_any_email_case(user):
    assert services.authenticate_user("U1@Test.com", "Passw0rd!") == user


@pytest.mark.django_db
def test_login_check_rejects_wrong_password(user):
    assert services.authenticate_user("u1@test.com", "wrong") is None


@pytest.mark.django_db
def test_login_check_rejects_unknown_email():
    assert services.authenticate_user("nobody@test.com", "Passw0rd!") is None


@pytest.mark.django_db
def test_login_check_rejects_disabled_account(user):
    user.is_active = False
    user.save()
    assert services.authenticate_user("u1@test.com", "Passw0rd!") is None
