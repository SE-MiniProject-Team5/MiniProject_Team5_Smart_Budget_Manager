import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from expenses.models import Expense
from budgets.alerts import evaluate_for_expense

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Expense)
def check_budget_alerts(sender, instance, created, **kwargs):
    """
    Evaluate budget alerts whenever an expense is saved.

    Alert failures must not prevent an expense from being saved.
    """
    try:
        evaluate_for_expense(instance)
    except Exception:
        logger.exception(
            "Failed to evaluate budget alerts for expense %s",
            instance.pk,
        )