"""FR-018: CSV export of the caller's expenses for a chosen period."""
import csv
import io

import pytest

from accounts.models import User
from expenses.models import Expense

URL = "/api/v1/reports/export/"


def rows(response):
    return list(csv.reader(io.StringIO(response.content.decode())))


@pytest.mark.django_db
def test_export_returns_csv_of_own_expenses_in_range(api, user, category):
    stranger = User.objects.create_user(username="b@test.com", email="b@test.com", password="Passw0rd!")
    Expense.objects.create(user=user, category=category, amount="120.00", expense_date="2026-01-10", note="lunch")
    Expense.objects.create(user=user, category=category, amount="80.50", expense_date="2026-01-03")
    Expense.objects.create(user=user, category=category, amount="999.00", expense_date="2026-02-01")
    Expense.objects.create(user=stranger, category=category, amount="555.00", expense_date="2026-01-10")
    api.force_authenticate(user=user)
    response = api.get(URL, {"from": "2026-01-01", "to": "2026-01-31"})
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert 'filename="smartspend_2026-01-01_2026-01-31.csv"' in response["Content-Disposition"]
    assert rows(response) == [
        ["date", "category", "amount", "note"],
        ["2026-01-03", "Food", "80.50", ""],
        ["2026-01-10", "Food", "120.00", "lunch"],
    ]


@pytest.mark.django_db
def test_formula_like_text_is_neutralised(api, user, category):
    Expense.objects.create(user=user, category=category, amount="1.00", expense_date="2026-01-10", note="=HYPERLINK(1)")
    api.force_authenticate(user=user)
    assert rows(api.get(URL, {"from": "2026-01-01", "to": "2026-01-31"}))[1][3] == "'=HYPERLINK(1)"


@pytest.mark.django_db
def test_export_bad_dates_give_400(api, user):
    api.force_authenticate(user=user)
    assert api.get(URL, {"from": "2026-01-01"}).status_code == 400


@pytest.mark.django_db
def test_export_needs_login(api):
    assert api.get(URL, {"from": "2026-01-01", "to": "2026-01-31"}).status_code == 401
