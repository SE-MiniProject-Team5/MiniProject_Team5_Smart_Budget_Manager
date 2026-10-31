import pytest

from budgets.models import Alert, Budget


@pytest.mark.django_db
def test_warning_alert_creation(user, category):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="1000.00",
        start_date="2026-10-01",
    )

    alert = Alert.objects.create(
        user=user,
        budget=budget,
        threshold_type=Alert.Threshold.WARNING_80,
    )

    assert alert.user == user
    assert alert.budget == budget
    assert alert.threshold_type == "80"
    assert alert.acknowledged is False
    assert alert.created_at is not None


@pytest.mark.django_db
def test_exceeded_budget_alert_creation(user, category):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="1000.00",
        start_date="2026-10-01",
    )

    alert = Alert.objects.create(
        user=user,
        budget=budget,
        threshold_type=Alert.Threshold.EXCEEDED_100,
    )

    assert alert.threshold_type == "100"
    assert alert.acknowledged is False


@pytest.mark.django_db
def test_alert_can_be_acknowledged(user, category):
    budget = Budget.objects.create(
        user=user,
        category=category,
        period="MONTHLY",
        limit_amount="1000.00",
        start_date="2026-10-01",
    )

    alert = Alert.objects.create(
        user=user,
        budget=budget,
        threshold_type=Alert.Threshold.WARNING_80,
    )

    alert.acknowledged = True
    alert.save()

    alert.refresh_from_db()

    assert alert.acknowledged is True