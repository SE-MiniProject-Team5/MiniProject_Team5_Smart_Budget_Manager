import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    """Predefined (owner is null) or user-created category (FR-007, FR-019)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)  # FR-007: custom name max 50 chars
    is_active = models.BooleanField(default=True)  # business rule: only active categories selectable
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="categories"
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    """A single recorded expense (FR-005, FR-006, FR-008). Field layout follows SRS Appendix B."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="expenses")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]  # FR-008: amount > 0
    )
    expense_date = models.DateField()
    note = models.CharField(max_length=255, blank=True, validators=[MaxLengthValidator(255)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expense_date} {self.amount}"
