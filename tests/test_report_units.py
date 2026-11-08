"""TEST-M4: unit tests for the reports module (analytics, trend, export, admin).

They call the report functions directly instead of going through the API.
"""
from datetime import date

import pytest

from accounts.models import User
from expenses.models import Category, Expense
from reports import services
from reports.serializers import AdminCategorySerializer
from reports.views import safe_cell


def spend(user, category, amount, day):
    Expense.objects.bulk_create([Expense(user=user, category=category, amount=amount, expense_date=day)])


@pytest.fixture
def travel(db):
    return Category.objects.create(name="Travel")


# ---- category_breakdown (FR-016) ----

@pytest.mark.django_db
def test_breakdown_is_largest_first_with_grand_total(user, category, travel):
    spend(user, category, "10.00", date(2026, 1, 2))
    spend(user, travel, "40.00", date(2026, 1, 3))
    spend(user, category, "5.00", date(2026, 1, 4))
    rows, total = services.category_breakdown(user, date(2026, 1, 1), date(2026, 1, 31))
    assert [(r["category"], r["total"]) for r in rows] == [("Travel", "40.00"), ("Food", "15.00")]
    assert total == "55.00"


@pytest.mark.django_db
def test_breakdown_of_empty_range_is_zero(user):
    rows, total = services.category_breakdown(user, date(2026, 1, 1), date(2026, 1, 31))
    assert rows == [] and total == "0.00"


# ---- spend_trend (FR-017) ----

@pytest.mark.django_db
def test_daily_trend_lists_every_day_with_zeros(user, category):
    spend(user, category, "8.00", date(2026, 1, 2))
    trend = services.spend_trend(user, date(2026, 1, 1), date(2026, 1, 3), "daily")
    assert [t["total"] for t in trend] == ["0.00", "8.00", "0.00"]


@pytest.mark.django_db
def test_weekly_trend_groups_from_monday(user, category):
    spend(user, category, "3.00", date(2026, 1, 4))  # Sunday
    spend(user, category, "4.00", date(2026, 1, 5))  # Monday
    trend = services.spend_trend(user, date(2026, 1, 1), date(2026, 1, 11), "weekly")
    assert [(t["period_start"], t["total"]) for t in trend] == [
        (date(2025, 12, 29), "3.00"),
        (date(2026, 1, 5), "4.00"),
    ]


# ---- expenses_for_export and safe_cell (FR-018) ----

@pytest.mark.django_db
def test_export_rows_are_oldest_first_and_inside_range(user, category):
    spend(user, category, "2.00", date(2026, 1, 9))
    spend(user, category, "1.00", date(2026, 1, 1))
    spend(user, category, "9.00", date(2026, 2, 1))
    rows = services.expenses_for_export(user, date(2026, 1, 1), date(2026, 1, 31))
    assert [str(e.amount) for e in rows] == ["1.00", "2.00"]


@pytest.mark.parametrize("text", ["=SUM(A1)", "+1", "-1", "@cmd"])
def test_safe_cell_disarms_formulas(text):
    assert safe_cell(text) == "'" + text


def test_safe_cell_leaves_normal_text_alone():
    assert safe_cell("lunch") == "lunch"
    assert safe_cell("") == ""


# ---- admin_usage_stats (FR-020) ----

@pytest.mark.django_db
def test_usage_stats_are_counts_only(user, category, travel):
    User.objects.create_user(username="x@test.com", email="x@test.com", password="Passw0rd!", is_active=False)
    spend(user, category, "1.00", date(2026, 1, 1))
    stats = services.admin_usage_stats()
    assert stats == {
        "total_users": 2,
        "active_users": 1,
        "total_expenses": 1,
        "categories_in_use": 1,
        "active_predefined_categories": 2,
    }


# ---- AdminCategorySerializer (FR-019) ----

def test_admin_category_name_is_trimmed():
    serializer = AdminCategorySerializer(data={"name": "  Rent  "})
    assert serializer.is_valid()
    assert serializer.validated_data["name"] == "Rent"


@pytest.mark.parametrize("name", ["   ", "<b>Rent</b>"])
def test_admin_category_bad_names_are_refused(name):
    assert not AdminCategorySerializer(data={"name": name}).is_valid()
