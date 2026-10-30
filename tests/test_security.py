import logging

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.models import User
from smartspend.permissions import IsAdminRole
from smartspend.security_log import log_security_event


PATH = "/api/v1/admin/analytics/"


class AdminOnlyView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response({"ok": True})


def call(user=None):
    factory = APIRequestFactory()
    request = factory.get(PATH)

    if user:
        force_authenticate(request, user=user)

    return AdminOnlyView.as_view()(request)


@pytest.mark.django_db
def test_regular_user_gets_403_and_is_logged(user, caplog):
    caplog.set_level(logging.WARNING, logger="security")

    response = call(user)

    assert response.status_code == 403
    assert (
        f"event=unauthorized_admin_access account={user.email} endpoint={PATH}"
        in caplog.text
    )
    assert "Passw0rd!" not in caplog.text


@pytest.mark.django_db
def test_admin_user_is_allowed():
    admin = User.objects.create_user(
        username="admin@test.com",
        email="admin@test.com",
        password="Passw0rd!",
        role=User.Role.ADMIN,
    )

    response = call(admin)

    assert response.status_code == 200


def test_anonymous_is_refused_and_logged(caplog):
    caplog.set_level(logging.WARNING, logger="security")

    response = call()

    assert response.status_code in (401, 403)
    assert "account=anonymous" in caplog.text


def test_log_entry_has_timestamp_account_and_endpoint(caplog):
    caplog.set_level(logging.WARNING, logger="security")

    log_security_event(
        "failed_login",
        "a@test.com",
        "/api/v1/auth/login/",
    )

    record = caplog.records[-1]

    assert record.created > 0
    assert record.getMessage() == (
        "event=failed_login account=a@test.com "
        "endpoint=/api/v1/auth/login/"
    )