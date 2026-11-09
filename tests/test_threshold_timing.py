"""TC-NFR-01 (FR-011, NFR-002): after an expense is saved, the budget's cumulative
spend and alerts are up to date within 1 second.

The test saves an expense through the API, then asks for the budget straight
away and measures how long it takes until the new total is shown.
"""
import time

import pytest

from budgets.models import Alert, Budget

LIMIT_SECONDS = 1.0  # FR-011 / NFR-002


@pytest.mark.django_db
def test_spend_and_alert_update_within_one_second(api, user, category):
    budget = Budget.objects.create(
        user=user, category=category, period="MONTHLY", limit_amount="1000.00", start_date="2026-01-01"
    )
    api.force_authenticate(user=user)
    api.post(
        "/api/v1/expenses/",
        {"category": str(category.id), "amount": "700.00", "expense_date": "2026-01-05"},
        format="json",
    )

    started = time.perf_counter()
    response = api.post(
        "/api/v1/expenses/",
        {"category": str(category.id), "amount": "100.00", "expense_date": "2026-01-06"},
        format="json",
    )
    body = api.get(f"/api/v1/budgets/{budget.id}/").json()
    elapsed = time.perf_counter() - started

    assert response.status_code == 201
    assert body["spent"] == "800.00"
    assert Alert.objects.filter(budget=budget, threshold_type="80").exists()
    assert elapsed < LIMIT_SECONDS