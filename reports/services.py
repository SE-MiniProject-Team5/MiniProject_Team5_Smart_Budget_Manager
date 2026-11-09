"""Report Service (SAD 3.1): spend analytics, exports and admin usage figures (FR-016 to FR-020)."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum

from expenses.models import Category, Expense


def category_breakdown(user, start, end):
    """Total spend per category for this user between start and end (both days included),
    largest first. Returns (rows, grand_total)."""
    rows = (
        Expense.objects.filter(user=user, expense_date__gte=start, expense_date__lte=end)
        .values("category_id", "category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    )
    breakdown = [
        {"category_id": str(r["category_id"]), "category": r["category__name"], "total": f"{r['total']:.2f}"}
        for r in rows
    ]
    grand_total = sum((r["total"] for r in rows), Decimal("0.00"))
    return breakdown, f"{grand_total:.2f}"


def spend_trend(user, start, end, granularity):
    """Spend per day or per week (weeks start on Monday) for this user, for a trend chart (FR-017).

    Every day or week in the range is listed, with 0.00 when nothing was spent,
    so the chart has no gaps.
    """
    daily = dict(
        Expense.objects.filter(user=user, expense_date__gte=start, expense_date__lte=end)
        .values_list("expense_date")
        .annotate(total=Sum("amount"))
    )
    totals = {}
    day = start
    while day <= end:
        bucket = day if granularity == "daily" else day - timedelta(days=day.weekday())
        totals[bucket] = totals.get(bucket, Decimal("0.00")) + daily.get(day, Decimal("0.00"))
        day += timedelta(days=1)
    return [{"period_start": bucket, "total": f"{total:.2f}"} for bucket, total in totals.items()]


def expenses_for_export(user, start, end):
    """The user's expenses in the range, oldest first, for the CSV export (FR-018)."""
    return (
        Expense.objects.filter(user=user, expense_date__gte=start, expense_date__lte=end)
        .select_related("category")
        .order_by("expense_date", "created_at")
    )


def admin_usage_stats():
    """System-wide totals for administrators (FR-020). Counts only: no names, emails or amounts per user."""
    users = get_user_model().objects
    return {
        "total_users": users.count(),
        "active_users": users.filter(is_active=True).count(),
        "total_expenses": Expense.objects.count(),
        "categories_in_use": Expense.objects.values("category_id").distinct().count(),
        "active_predefined_categories": Category.objects.filter(owner__isnull=True, is_active=True).count(),
    }
