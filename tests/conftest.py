"""Shared pytest fixtures. A fixture is a ready-made object a test asks for
by naming it as an argument."""
import pytest
from rest_framework.test import APIClient
from accounts.models import User
from expenses.models import Category

@pytest.fixture
def api():
    """A DRF test client for calling /api/v1/... endpoints."""
    return APIClient()
@pytest.fixture
def user(db):
    """A saved regular user (role USER)."""
    return User.objects.create_user(username="u1@test.com",
email="u1@test.com", password="Passw0rd!")
@pytest.fixture
def category(db):
    """A saved, active, predefined category."""
    return Category.objects.create(name="Food") 