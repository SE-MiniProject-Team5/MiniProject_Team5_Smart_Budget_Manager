"""FR-017: spend trend data for a daily or weekly chart."""
import pytest

from expenses.models import Expense

URL = "/api/v1/analytics/trend/"


@pytest.mark.django_db
def test_daily_trend_lists_every_day_with_zeros(api, user, category):
    Expense.objects.create(user=user, category=category, amount="100.00", expense_date="2026-01-02")
    Expense.objects.create(user=user, category=category, amount="50.00", expense_date="2026-01-02")
    Expense.objects.create(user=user, category=category, amount="20.00", expense_date="2026-01-04")
    api.force_authenticate(user=user)
    body = api.get(URL, {"from": "2026-01-01", "to": "2026-01-04"}).json()
    assert body["granularity"] == "daily"
    assert [(p["period_start"], p["total"]) for p in body["points"]] == [
        ("2026-01-01", "0.00"),
        ("2026-01-02", "150.00"),
        ("2026-01-03", "0.00"),
        ("2026-01-04", "20.00"),
    ]


@pytest.mark.django_db
def test_weekly_trend_groups_by_monday(api, user, category):
    # 2026-01-05 and 2026-01-12 are Mondays
    Expense.objects.create(user=user, category=category, amount="10.00", expense_date="2026-01-05")
    Expense.objects.create(user=user, category=category, amount="15.00", expense_date="2026-01-11")
    Expense.objects.create(user=user, category=category, amount="40.00", expense_date="2026-01-12")
    api.force_authenticate(user=user)
    body = api.get(URL, {"from": "2026-01-05", "to": "2026-01-18", "granularity": "weekly"}).json()
    assert [(p["period_start"], p["total"]) for p in body["points"]] == [("2026-01-05", "25.00"), ("2026-01-12", "40.00")]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"from": "2026-01-01", "to": "2026-01-31", "granularity": "monthly"},
        {"from": "2025-01-01", "to": "2026-06-30"},
        {"from": "2026-02-01", "to": "2026-01-01"},
        {},
    ],
)
def test_bad_parameters_give_400(api, user, params):
    api.force_authenticate(user=user)
    assert api.get(URL, params).status_code == 400


@pytest.mark.django_db
def test_trend_needs_login(api):
    assert api.get(URL, {"from": "2026-01-01", "to": "2026-01-02"}).status_code == 401
