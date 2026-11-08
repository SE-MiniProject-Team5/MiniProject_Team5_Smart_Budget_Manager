"""FR-015: an alert can be acknowledged and then no longer shows as active."""
import pytest

from accounts.models import User
from budgets.models import Alert, Budget


@pytest.fixture
def alert(user, category):
    budget = Budget.objects.create(
        user=user, category=category, period="MONTHLY", limit_amount="1000.00", start_date="2026-01-01"
    )
    return Alert.objects.create(user=user, budget=budget, threshold_type="80")


def url(alert):
    return f"/api/v1/alerts/{alert.id}/acknowledge/"


@pytest.mark.django_db
def test_acknowledge_hides_alert(api, user, alert):
    api.force_authenticate(user=user)
    response = api.post(url(alert))
    assert response.status_code == 200
    assert response.json()["acknowledged"] is True
    assert api.get("/api/v1/alerts/").json() == []


@pytest.mark.django_db
def test_cannot_acknowledge_someone_elses_alert(api, alert):
    stranger = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    api.force_authenticate(user=stranger)
    assert api.post(url(alert)).status_code == 404
    alert.refresh_from_db()
    assert alert.acknowledged is False


@pytest.mark.django_db
def test_acknowledging_does_not_recreate_the_alert(api, user, category, alert):
    api.force_authenticate(user=user)
    api.post(url(alert))
    api.post(
        "/api/v1/expenses/",
        {"category": str(category.id), "amount": "900.00", "expense_date": "2026-01-10"},
        format="json",
    )
    assert Alert.objects.filter(threshold_type="80").count() == 1
