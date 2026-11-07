"""Sprint 1 demo (DOC-05): calls the running SmartSpend API step by step.

Start the server first in another window:  python manage.py runserver
Then run:                                  python docs/demo/sprint1_demo.py
Uses only the Python standard library.
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
EMAIL = f"demo-{uuid.uuid4().hex[:6]}@smartspend.test"  # a fresh user every run
PASSWORD = "Passw0rd!"


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request) as response:
            status, text = response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        status, text = error.code, error.read().decode()
    except urllib.error.URLError:
        sys.exit("Cannot reach the server. Start it first with: python manage.py runserver")
    return status, (json.loads(text) if text else None)


def step(title, method, path, body=None, token=None):
    print(f"\n=== {title}")
    print(f"{method} /api/v1{path}")
    status, result = call(method, path, body, token)
    print(f"-> {status}")
    shown = dict(result) if isinstance(result, dict) else result
    if isinstance(shown, dict) and "token" in shown:
        shown["token"] = shown["token"][:20] + "..."
    print(json.dumps(shown, indent=2))
    time.sleep(2.5)  # time to read it in the video
    return status, result


print("SmartSpend - Team H5 - Sprint 1 demo")
step("1. Register a new user (FR-001)", "POST", "/auth/register/", {"email": EMAIL, "password": PASSWORD})
step("2. Same email again is rejected (FR-002)", "POST", "/auth/register/", {"email": EMAIL, "password": PASSWORD})
_, login = step("3. Log in and get a 24-hour token (FR-003, FR-004)", "POST", "/auth/login/", {"email": EMAIL, "password": PASSWORD})
token = login["token"]
step("4. A bad token is rejected (SEC-004)", "GET", "/expenses/", token="not-a-real-token")
_, food = step("5. Create a category (FR-007)", "POST", "/categories/", {"name": "Food"}, token)
_, travel = step("6. Create a second category", "POST", "/categories/", {"name": "Travel"}, token)
today = time.strftime("%Y-%m-%d")
month_start = time.strftime("%Y-%m-01")
step("7. Add an expense (FR-005)", "POST", "/expenses/", {"category": food["id"], "amount": "250.00", "expense_date": today, "note": "lunch"}, token)
step("8. Add another expense", "POST", "/expenses/", {"category": travel["id"], "amount": "400.00", "expense_date": today, "note": "bus pass"}, token)
step("9. Amount 0 is rejected (FR-008)", "POST", "/expenses/", {"category": food["id"], "amount": "0", "expense_date": today}, token)
_, budget = step("10. Create a monthly Food budget (FR-009)", "POST", "/budgets/", {"category": food["id"], "period": "MONTHLY", "limit_amount": "1000.00", "start_date": month_start}, token)
step("11. An overlapping budget is rejected (FR-012)", "POST", "/budgets/", {"category": food["id"], "period": "MONTHLY", "limit_amount": "500.00", "start_date": month_start}, token)
step("12. Budget shows spent and remaining (FR-011)", "GET", f"/budgets/{budget['id']}/", token=token)
step("13. Spend by category this month (FR-016)", "GET", f"/analytics/?from={month_start}&to={today}", token=token)
print("\nDemo complete.")