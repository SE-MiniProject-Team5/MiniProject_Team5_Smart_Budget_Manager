"""FR-007: pick a predefined category or create a custom one (max 50 characters)."""
import pytest

from accounts.models import User
from expenses.models import Category

URL = "/api/v1/categories/"


@pytest.mark.django_db
def test_list_shows_predefined_and_own_active_categories(api, user, category):
    other = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    Category.objects.create(name="Mine", owner=user)
    Category.objects.create(name="Theirs", owner=other)
    Category.objects.create(name="Retired", is_active=False)
    api.force_authenticate(user=user)
    names = [row["name"] for row in api.get(URL).json()]
    assert names == ["Food", "Mine"]


@pytest.mark.django_db
def test_create_custom_category(api, user):
    api.force_authenticate(user=user)
    response = api.post(URL, {"name": "Books"}, format="json")
    assert response.status_code == 201
    assert response.json()["is_custom"] is True
    assert Category.objects.get(name="Books").owner == user


@pytest.mark.django_db
def test_name_longer_than_50_rejected(api, user):  # FR-007
    api.force_authenticate(user=user)
    response = api.post(URL, {"name": "x" * 51}, format="json")
    assert response.status_code == 400
    assert "name" in response.json()


@pytest.mark.django_db
def test_blank_name_rejected(api, user):
    api.force_authenticate(user=user)
    assert api.post(URL, {"name": "   "}, format="json").status_code == 400


@pytest.mark.django_db
def test_anonymous_caller_refused(api):
    assert api.get(URL).status_code in (401, 403)