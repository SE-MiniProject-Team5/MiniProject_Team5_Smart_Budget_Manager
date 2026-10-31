"""Object-level ownership check (FR-006, SRS 7.1 Integrity)."""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Only the user who owns a record may see, change or delete it. Anyone else gets 403."""

    message = "You can only access your own records."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id