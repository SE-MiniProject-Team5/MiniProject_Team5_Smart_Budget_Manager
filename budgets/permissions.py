
"""Object-level ownership check (FR-010, SRS 7.1 Integrity)."""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Only the user who owns a budget may see, change or delete it. Anyone
    else gets 403."""

    message = "You can only access your own budgets."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
