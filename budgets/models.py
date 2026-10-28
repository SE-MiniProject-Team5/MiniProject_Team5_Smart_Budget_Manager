import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Budget(models.Model):
    """Spending limit per category and period (FR-009, FR-010, FR-012)."""

    class Period(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey("expenses.Category", on_delete=models.PROTECT, related_name="budgets")
    limit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    period = models.CharField(max_length=10, choices=Period.choices)
    start_date = models.DateField()

    def __str__(self):
        return f"{self.category} {self.period} {self.limit_amount}"


class Alert(models.Model):
    """Threshold alert (FR-013, FR-014, FR-015)."""

    class Threshold(models.TextChoices):
        WARNING_80 = "80", "80% of budget reached"
        EXCEEDED_100 = "100", "Budget exceeded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alerts")
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="alerts")
    threshold_type = models.CharField(max_length=3, choices=Threshold.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
