
from calendar import monthrange
from datetime import timedelta

from .models import Budget


def budget_end_date(start_date, period):
    """Calculate the inclusive end date of a budget period."""

    if period == Budget.Period.WEEKLY:
        return start_date + timedelta(days=6)

    if period == Budget.Period.MONTHLY:
        last_day = monthrange(start_date.year, start_date.month)[1]
        return start_date.replace(day=last_day)

    raise ValueError("Invalid budget period.")


def has_overlapping_budget(user, category, period, start_date):
    """Check whether this user already has an overlapping budget."""

    new_end = budget_end_date(start_date, period)

    existing_budgets = Budget.objects.filter(
        user=user,
        category=category,
    )

    for existing in existing_budgets:
        existing_end = budget_end_date(
            existing.start_date,
            existing.period,
        )

        if start_date <= existing_end and existing.start_date <= new_end:
            return True

    return False
