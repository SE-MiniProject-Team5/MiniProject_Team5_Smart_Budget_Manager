"""Budget business rules (SAD 3.1 Budget Service): period end dates and the
overlap rule (FR-012)."""
import calendar
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum

from expenses.models import Expense

from .models import Budget


def end_date(period, start):
    """Last day a budget covers: weekly = start + 6 days, monthly = last day
    of the start month."""
    if period == Budget.Period.WEEKLY:
        return start + timedelta(days=6)
    last_day = calendar.monthrange(start.year, start.month)[1]
    return start.replace(day=last_day)


def overlaps_existing(user, category, period, start, exclude_id=None):
    """True if this user already has a budget for this category whose dates
    overlap the new one.

    exclude_id skips one budget: the one being edited, so it does not clash
    with itself (FR-010).
    """
    new_end = end_date(period, start)
    others = Budget.objects.filter(user=user, category=category)
    if exclude_id is not None:
        others = others.exclude(id=exclude_id)
    for old in others:
        old_end = end_date(old.period, old.start_date)
        if start <= old_end and old.start_date <= new_end:
            return True
    return False


def category_problem(category, user):
    """Same rule as expenses (SRS 6.5): only active categories, predefined or
    the user's own."""
    if not category.is_active:
        return "This category is inactive and cannot be used."
    if category.owner_id is not None and category.owner_id != user.id:
        return "You can only use predefined categories or your own."
    return None


def spent_for(budget):
    """Cumulative spend against a budget (FR-011): the owner's expenses in
    that category whose date falls inside the budget period. Computed from
    the database on every request, so a newly saved expense is reflected
    immediately (NFR-002: within 1 second)."""
    total = Expense.objects.filter(
        user_id=budget.user_id,
        category_id=budget.category_id,
        expense_date__gte=budget.start_date,
        expense_date__lte=end_date(budget.period, budget.start_date),
    ).aggregate(total=Sum("amount"))["total"]
    return total or Decimal("0.00")
