from datetime import date
from decimal import Decimal

import pytest

from budgets.models import Budget
from budgets.services import spent_for
from expenses.models import Expense


@pytest.mark.django_db
def test_spent_and_remaining_are_returned(user, category):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    Expense.objects.create(
        user=user,
        category=category,
        amount=Decimal("250.00"),
        expense_date=date(2026, 10, 12),
    )

    spent = spent_for(budget)
    remaining = budget.limit_amount - spent

    assert spent == Decimal("250.00")
    assert remaining == Decimal("750.00")


@pytest.mark.django_db
def test_new_expense_is_reflected_on_next_request(user, category):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    first_spent = spent_for(budget)
    assert first_spent == Decimal("0.00")

    Expense.objects.create(
        user=user,
        category=category,
        amount=Decimal("300.00"),
        expense_date=date(2026, 10, 15),
    )

    second_spent = spent_for(budget)
    assert second_spent == Decimal("300.00")