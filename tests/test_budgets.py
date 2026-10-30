
from datetime import date

import pytest
from rest_framework.test import APIClient

from budgets.models import Budget
from accounts.models import User
from expenses.models import Category


@pytest.fixture
def authenticated_api(api, user):
    api.force_authenticate(user=user)
    return api


def test_create_monthly_budget(authenticated_api, category):
    response = authenticated_api.post(
        "/api/v1/budgets/",
        {
            "category": str(category.id),
            "period": "MONTHLY",
            "limit_amount": "5000.00",
            "start_date": "2026-10-01",
        },
    )
    assert response.status_code == 201


def test_zero_budget_limit_rejected(authenticated_api, category):
    response = authenticated_api.post(
        "/api/v1/budgets/",
        {
            "category": str(category.id),
            "period": "MONTHLY",
            "limit_amount": "0",
            "start_date": "2026-10-01",
        },
    )
    assert response.status_code == 400


def test_negative_budget_limit_rejected(authenticated_api, category):
    response = authenticated_api.post(
        "/api/v1/budgets/",
        {
            "category": str(category.id),
            "period": "MONTHLY",
            "limit_amount": "-100",
            "start_date": "2026-10-01",
        },
    )
    assert response.status_code == 400


def test_second_budget_same_month_rejected(authenticated_api, user, category):
    Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="5000",
        start_date=date(2026, 10, 1),
    )

    response = authenticated_api.post(
        "/api/v1/budgets/",
        {
            "category": str(category.id),
            "period": "MONTHLY",
            "limit_amount": "6000",
            "start_date": "2026-10-15",
        },
    )
    assert response.status_code == 409


def test_weekly_inside_monthly_rejected(authenticated_api, user, category):
    Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="5000",
        start_date=date(2026, 10, 1),
    )

    response = authenticated_api.post(
        "/api/v1/budgets/",
        {
            "category": str(category.id),
            "period": "WEEKLY",
            "limit_amount": "1000",
            "start_date": "2026-10-12",
        },
    )
    assert response.status_code == 409


def test_next_month_is_allowed(authenticated_api, user, category):
    Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="5000",
        start_date=date(2026, 10, 1),
    )

    response = authenticated_api.post(
        "/api/v1/budgets/",
        {
            "category": str(category.id),
            "period": "MONTHLY",
            "limit_amount": "6000",
            "start_date": "2026-11-01",
        },
    )
    assert response.status_code == 201
