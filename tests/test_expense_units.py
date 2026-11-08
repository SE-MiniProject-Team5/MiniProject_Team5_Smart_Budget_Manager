"""TEST-M2: unit tests for the expenses module, part 1: the text sanitiser,
the category rule and the models. They call the code directly, not the API."""
import pytest
from rest_framework import serializers

from accounts.models import User
from expenses.models import Category, Expense
from expenses.services import category_problem
from expenses.validators import clean_text


# ---- clean_text (SEC-003) ----

def test_clean_text_trims_spaces():
    assert clean_text("  lunch  ") == "lunch"


def test_clean_text_keeps_normal_punctuation():
    assert clean_text("Tea & snacks, 2 cups (office)") == "Tea & snacks, 2 cups (office)"


@pytest.mark.parametrize("bad", ["a\tb", "a\nb", "a\x00b", "a\x7fb"])
def test_clean_text_rejects_control_characters(bad):
    with pytest.raises(serializers.ValidationError):
        clean_text(bad)


@pytest.mark.parametrize("bad", ["<b>", "a < b", "x>y"])
def test_clean_text_rejects_angle_brackets(bad):
    with pytest.raises(serializers.ValidationError):
        clean_text(bad)


# ---- category_problem (SRS 6.5 business rule) ----

@pytest.mark.django_db
def test_active_predefined_category_is_allowed(user, category):
    assert category_problem(category, user) is None


@pytest.mark.django_db
def test_inactive_category_is_refused(user, category):
    category.is_active = False
    assert "inactive" in category_problem(category, user)


@pytest.mark.django_db
def test_own_custom_category_is_allowed(user):
    own = Category.objects.create(name="Gym", owner=user)
    assert category_problem(own, user) is None


@pytest.mark.django_db
def test_someone_elses_category_is_refused(user):
    other = User.objects.create_user(username="o@test.com", email="o@test.com", password="Passw0rd!")
    theirs = Category.objects.create(name="Theirs", owner=other)
    assert "own" in category_problem(theirs, user)


# ---- models ----

@pytest.mark.django_db
def test_category_is_shown_by_name(category):
    assert str(category) == "Food"


@pytest.mark.django_db
def test_expense_is_shown_by_date_and_amount(user, category):
    expense = Expense.objects.create(user=user, category=category, amount="12.50", expense_date="2026-01-05")
    assert str(expense) == "2026-01-05 12.50"
