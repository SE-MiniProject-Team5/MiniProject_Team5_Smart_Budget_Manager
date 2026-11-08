"""TEST-M3: unit tests for the budgets module (budgets and alerts).

They call the budget rules directly instead of going through the API:
period end dates, the overlap rule, spend totals, serializer checks and the
Alert Engine's 80% / 100% boundaries.
"""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from accounts.models import User
from budgets import services
from budgets.alerts import evaluate_budget
from budgets.models import Alert, Budget
from budgets.serializers import BudgetSerializer
from expenses.models import Category, Expense


def make_budget(user, category, limit="100.00", period="MONTHLY", start=date(2026, 1, 1)):
    return Budget.objects.create(user=user, category=category, period=period, limit_amount=Decimal(limit), start_date=start)


def spend(user, category, amount, day=date(2026, 1, 10)):
    # bulk_create skips the post_save signal, so the Alert Engine is only run when a test calls it.
    Expense.objects.bulk_create([Expense(user=user, category=category, amount=amount, expense_date=day)])


# ---- services.end_date (FR-009) ----

def test_weekly_budget_ends_six_days_later():
    assert services.end_date(Budget.Period.WEEKLY, date(2026, 1, 5)) == date(2026, 1, 11)


def test_monthly_budget_ends_on_last_day_of_month():
    assert services.end_date(Budget.Period.MONTHLY, date(2026, 2, 10)) == date(2026, 2, 28)


def test_monthly_budget_in_leap_year_february():
    assert services.end_date(Budget.Period.MONTHLY, date(2028, 2, 1)) == date(2028, 2, 29)


# ---- services.overlaps_existing (FR-012) ----

@pytest.mark.django_db
def test_overlapping_budget_is_detected(user, category):
    make_budget(user, category)
    assert services.overlaps_existing(user, category, "WEEKLY", date(2026, 1, 20))


@pytest.mark.django_db
def test_next_month_does_not_overlap(user, category):
    make_budget(user, category)
    assert not services.overlaps_existing(user, category, "MONTHLY", date(2026, 2, 1))


@pytest.mark.django_db
def test_budget_being_edited_does_not_clash_with_itself(user, category):
    budget = make_budget(user, category)
    assert not services.overlaps_existing(user, category, "MONTHLY", date(2026, 1, 1), exclude_id=budget.id)


# ---- services.category_problem (SRS 6.5) ----

def test_category_rule_allows_active_predefined():
    category = SimpleNamespace(is_active=True, owner_id=None)
    assert services.category_problem(category, SimpleNamespace(id=1)) is None


def test_category_rule_refuses_inactive():
    category = SimpleNamespace(is_active=False, owner_id=None)
    assert "inactive" in services.category_problem(category, SimpleNamespace(id=1))


def test_category_rule_refuses_someone_elses():
    category = SimpleNamespace(is_active=True, owner_id=2)
    assert "own" in services.category_problem(category, SimpleNamespace(id=1))


# ---- services.spent_for (FR-011) ----

@pytest.mark.django_db
def test_spent_counts_only_this_budgets_period_category_and_user(user, category):
    budget = make_budget(user, category)
    other_user = User.objects.create_user(username="o@test.com", email="o@test.com", password="Passw0rd!")
    other_category = Category.objects.create(name="Travel")
    spend(user, category, "30.00")
    spend(user, category, "5.00", day=date(2026, 2, 1))  # next month
    spend(user, other_category, "7.00")
    spend(other_user, category, "9.00")
    assert services.spent_for(budget) == Decimal("30.00")


@pytest.mark.django_db
def test_spent_is_zero_with_no_expenses(user, category):
    assert services.spent_for(make_budget(user, category)) == Decimal("0.00")


# ---- serializer checks that the API field types normally catch first ----

def test_serializer_refuses_zero_limit():
    with pytest.raises(Exception):
        BudgetSerializer().validate_limit_amount(Decimal("0"))


def test_serializer_refuses_unknown_period():
    with pytest.raises(Exception):
        BudgetSerializer().validate_period("DAILY")


@pytest.mark.django_db
def test_serializer_refuses_inactive_category(user):
    inactive = Category.objects.create(name="Old", is_active=False)
    request = SimpleNamespace(user=user)
    with pytest.raises(Exception):
        BudgetSerializer(context={"request": request}).validate_category(inactive)


# ---- Alert Engine boundaries (FR-013, FR-014) ----

@pytest.mark.django_db
def test_just_under_80_percent_gives_no_alert(user, category):
    budget = make_budget(user, category)
    spend(user, category, "79.99")
    assert evaluate_budget(budget) == []


@pytest.mark.django_db
def test_exactly_100_percent_gives_only_the_warning(user, category):
    budget = make_budget(user, category)
    spend(user, category, "100.00")
    created = evaluate_budget(budget)
    assert [a.threshold_type for a in created] == [Alert.Threshold.WARNING_80]


@pytest.mark.django_db
def test_jumping_past_100_percent_gives_both_alerts_once(user, category):
    budget = make_budget(user, category)
    spend(user, category, "150.00")
    assert len(evaluate_budget(budget)) == 2
    assert evaluate_budget(budget) == []  # running again creates nothing new


# ---- models ----

@pytest.mark.django_db
def test_budget_is_shown_by_category_period_and_limit(user, category):
    assert str(make_budget(user, category)) == "Food MONTHLY 100.00"
