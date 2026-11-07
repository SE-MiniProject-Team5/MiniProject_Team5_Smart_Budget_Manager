from decimal import Decimal

from budgets.models import Alert, Budget
from budgets.services import end_date, spent_for


def evaluate_budget(budget):
    """
    Evaluate spending against a budget and create threshold alerts.

    80% alert: spending is greater than or equal to 80%.
    100% alert: spending is strictly greater than 100%.
    Existing alerts are not duplicated.
    """
    spent = spent_for(budget)
    limit = budget.limit_amount

    if limit <= Decimal("0"):
        return []

    alerts = []

    thresholds = []

    if spent >= limit * Decimal("0.80"):
        thresholds.append(Alert.Threshold.WARNING_80)

    if spent > limit:
        thresholds.append(Alert.Threshold.EXCEEDED_100)

    for threshold in thresholds:
        alert, created = Alert.objects.get_or_create(
            budget=budget,
            threshold_type=threshold,
            defaults={"user": budget.user},
        )

        if created:
            alerts.append(alert)

    return alerts


def evaluate_for_expense(expense):
    """
    Evaluate all budgets matching the saved expense's user and category
    whose date range contains the expense date.
    """
    budgets = Budget.objects.filter(
        user=expense.user,
        category=expense.category,
        start_date__lte=expense.expense_date,
    )

    created_alerts = []

    for budget in budgets:
        budget_end = end_date(budget.period, budget.start_date)

        if expense.expense_date <= budget_end:
            created_alerts.extend(evaluate_budget(budget))

    return created_alerts