"""FR-015: active alerts are listed for the user on login or dashboard load."""
import pytest

from accounts.models import User
from budgets.models import Alert, Budget


@pytest.fixture
def budget(user, category):
    return Budget.objects.create(
        user=user, category=category, period="MONTHLY", limit_amount="1000.00", start_date="2026-01-01"
    )


@pytest.mark.django_db
def test_lists_only_own_unacknowledged_alerts(api, user, category, budget):
    stranger = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    theirs = Budget.objects.create(
        user=stranger, category=category, period="MONTHLY", limit_amount="10.00", start_date="2026-01-01"
    )
    mine = Alert.objects.create(user=user, budget=budget, threshold_type="80")
    Alert.objects.create(user=user, budget=budget, threshold_type="100", acknowledged=True)
    Alert.objects.create(user=stranger, budget=theirs, threshold_type="80")
    api.force_authenticate(user=user)
    rows = api.get("/api/v1/alerts/").json()
    assert [row["id"] for row in rows] == [str(mine.id)]
    assert rows[0]["message"] == "80% of budget reached"
    assert rows[0]["category"] == "Food"


@pytest.mark.django_db
def test_alert_shows_up_after_spending_through_the_api(api, user, category, budget):  # TC-FUN-06
    api.force_authenticate(user=user)
    api.post(
        "/api/v1/expenses/",
        {"category": str(category.id), "amount": "850.00", "expense_date": "2026-01-10"},
        format="json",
    )
    rows = api.get("/api/v1/alerts/").json()
    assert [row["threshold_type"] for row in rows] == ["80"]


@pytest.mark.django_db
def test_alerts_need_login(api):
    assert api.get("/api/v1/alerts/").status_code == 401
