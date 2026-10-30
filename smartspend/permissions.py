
"""Role-based access control for administrator endpoints (FR-021, SEC-002)."""

from rest_framework.permissions import BasePermission

from accounts.models import User
from .security_log import log_security_event


class IsAdminRole(BasePermission):
    """Allow only logged-in users whose role is ADMIN. Everyone else is refused and logged."""

    message = "Administrator role required."

    def has_permission(self, request, view):
        user = request.user

        if (
            user
            and user.is_authenticated
            and user.role == User.Role.ADMIN
        ):
            return True

        account = (
            user.email
            if user and user.is_authenticated
            else "anonymous"
        )

        log_security_event(
            "unauthorized_admin_access",
            account,
            request.path,
        )

        return False
