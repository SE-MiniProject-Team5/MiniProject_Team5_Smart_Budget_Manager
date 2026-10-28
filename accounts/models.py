import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user. Log in with email (FR-001..FR-004). Role drives RBAC (SEC-002)."""

    class Role(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Administrator"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)  # FR-002: duplicate email rejected
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
