"""FR-011: every budget returned by the API shows spent, remaining and its end date."""
import pytest

from budgets.models import Budget
from expenses.models import Expense


@pytest.mark.django_db
def test_budget_detail_shows_spent_and_remaining(api, user, category):
    budget = Budget.objects.create(
        user=user, category=category, period="MONTHLY", limit_amount="1000.00", start_date="2026-01-01"
    )
    Expense.objects.create(user=user, category=category, amount="250.00", expense_date="2026-01-12")
    api.force_authenticate(user=user)
    body = api.get(f"/api/v1/budgets/{budget.id}/").json()
    assert body["spent"] == "250.00"
    assert body["remaining"] == "750.00"
    assert body["end_date"] == "2026-01-31"


@pytest.mark.django_db
def test_new_budget_starts_with_nothing_spent(api, user, category):
    api.force_authenticate(user=user)
    response = api.post(
        "/api/v1/budgets/",
        {"category": str(category.id), "period": "WEEKLY", "limit_amount": "500.00", "start_date": "2026-01-05"},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["spent"] == "0.00"
    assert response.json()["end_date"] == "2026-01-11"
