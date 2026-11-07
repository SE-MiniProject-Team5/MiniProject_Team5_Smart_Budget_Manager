from datetime import date
from decimal import Decimal

import pytest

from budgets.models import Alert, Budget
from expenses.models import Expense


@pytest.mark.django_db
def test_expense_save_triggers_warning_alert(user, category):
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
        amount=Decimal("800.00"),
        expense_date=date(2026, 10, 10),
    )

    assert Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.WARNING_80,
    ).exists()


@pytest.mark.django_db
def test_expense_save_triggers_exceeded_alert(user, category):
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
        amount=Decimal("1100.00"),
        expense_date=date(2026, 10, 10),
    )

    assert Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.WARNING_80,
    ).exists()

    assert Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.EXCEEDED_100,
    ).exists()


@pytest.mark.django_db
def test_expense_save_succeeds_if_alert_evaluation_fails(
    user, category, monkeypatch
):
    from budgets import signals

    def failing_evaluation(expense):
        raise RuntimeError("Simulated alert failure")

    monkeypatch.setattr(
        signals,
        "evaluate_for_expense",
        failing_evaluation,
    )

    expense = Expense.objects.create(
        user=user,
        category=category,
        amount=Decimal("100.00"),
        expense_date=date(2026, 10, 10),
    )

    assert Expense.objects.filter(pk=expense.pk).exists()