"""Report Service (SAD 3.1): spend analytics for one user (FR-016)."""

from decimal import Decimal

from django.db.models import Sum

from expenses.models import Expense


def category_breakdown(user, start, end):
    """Total spend per category for this user between start and end (both
    days included), largest first. Returns (rows, grand_total).
    """
    rows = (
        Expense.objects.filter(
            user=user,
            expense_date__gte=start,
            expense_date__lte=end,
        )
        .values("category_id", "category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    )

    breakdown = [
        {
            "category_id": str(r["category_id"]),
            "category": r["category__name"],
            "total": f"{r['total']:.2f}",
        }
        for r in rows
    ]

    grand_total = sum((r["total"] for r in rows), Decimal("0.00"))

    return breakdown, f"{grand_total:.2f}"