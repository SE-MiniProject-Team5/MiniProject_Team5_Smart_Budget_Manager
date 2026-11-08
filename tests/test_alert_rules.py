from datetime import date
from decimal import Decimal

import pytest

from budgets.alerts import evaluate_budget, evaluate_for_expense
from budgets.models import Alert, Budget
from expenses.models import Expense


@pytest.mark.django_db
def test_warning_created_at_80_percent(user, category, monkeypatch):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    monkeypatch.setattr(
        "budgets.alerts.spent_for",
        lambda budget: Decimal("800.00"),
    )

    alerts = evaluate_budget(budget)

    assert len(alerts) == 1
    assert alerts[0].threshold_type == Alert.Threshold.WARNING_80


@pytest.mark.django_db
def test_no_alert_below_80_percent(user, category, monkeypatch):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    monkeypatch.setattr(
        "budgets.alerts.spent_for",
        lambda budget: Decimal("799.00"),
    )

    alerts = evaluate_budget(budget)

    assert alerts == []
    assert Alert.objects.filter(budget=budget).count() == 0


@pytest.mark.django_db
def test_exceeded_alert_above_100_percent(user, category, monkeypatch):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    monkeypatch.setattr(
        "budgets.alerts.spent_for",
        lambda budget: Decimal("1001.00"),
    )

    evaluate_budget(budget)

    assert Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.WARNING_80,
    ).exists()

    assert Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.EXCEEDED_100,
    ).exists()


@pytest.mark.django_db
def test_exactly_100_percent_does_not_create_exceeded_alert(
    user, category, monkeypatch
):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    monkeypatch.setattr(
        "budgets.alerts.spent_for",
        lambda budget: Decimal("1000.00"),
    )

    evaluate_budget(budget)

    assert Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.WARNING_80,
    ).exists()

    assert not Alert.objects.filter(
        budget=budget,
        threshold_type=Alert.Threshold.EXCEEDED_100,
    ).exists()


@pytest.mark.django_db
def test_alerts_are_not_duplicated(user, category, monkeypatch):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    monkeypatch.setattr(
        "budgets.alerts.spent_for",
        lambda budget: Decimal("850.00"),
    )

    first_result = evaluate_budget(budget)
    second_result = evaluate_budget(budget)

    assert len(first_result) == 1
    assert second_result == []
    assert Alert.objects.filter(budget=budget).count() == 1


@pytest.mark.django_db
def test_evaluate_for_expense_checks_matching_budget(
    user, category, monkeypatch
):
    from budgets import signals

    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount=Decimal("1000.00"),
        start_date=date(2026, 10, 1),
    )

    # Prevent the automatic signal from evaluating this expense
    # before this test explicitly calls evaluate_for_expense().
    monkeypatch.setattr(
        signals,
        "evaluate_for_expense",
        lambda expense: [],
    )

    expense = Expense.objects.create(
        user=user,
        category=category,
        amount=Decimal("800.00"),
        expense_date=date(2026, 10, 10),
    )

    alerts = evaluate_for_expense(expense)

    assert len(alerts) == 1
    assert alerts[0].budget == budget
    assert alerts[0].threshold_type == Alert.Threshold.WARNING_80
