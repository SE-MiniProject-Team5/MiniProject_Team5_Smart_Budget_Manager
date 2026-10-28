import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from accounts.models import User
from expenses.models import Category, Expense


def test_health_endpoint(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home_page_renders(client):
    assert client.get("/").status_code == 200


@pytest.mark.django_db
def test_duplicate_email_rejected():  # FR-002
    User.objects.create_user(username="a", email="a@test.com", password="Passw0rd!")
    with pytest.raises(IntegrityError):
        User.objects.create_user(username="b", email="a@test.com", password="Passw0rd!")


@pytest.mark.django_db
def test_expense_amount_must_be_positive():  # FR-008
    user = User.objects.create_user(username="a", email="a@test.com", password="Passw0rd!")
    cat = Category.objects.create(name="Food")
    bad = Expense(user=user, category=cat, amount=0, expense_date="2026-10-27")
    with pytest.raises(ValidationError):
        bad.full_clean()
