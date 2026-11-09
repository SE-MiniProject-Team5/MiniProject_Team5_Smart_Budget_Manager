"""Sprint 2 demo (DOC-03): calls the running SmartSpend API step by step.

Start the server first in another window:  python manage.py runserver
Then run, from the repo folder:            python docs/demo/sprint2_demo.py
Uses only the Python standard library. Each run makes a fresh user and a fresh admin.
"""
import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
REPO = pathlib.Path(__file__).resolve().parents[2]  # the folder with manage.py
RUN = uuid.uuid4().hex[:6]
EMAIL = f"demo-{RUN}@smartspend.test"
ADMIN_EMAIL = f"admin-{RUN}@smartspend.test"
PASSWORD = "Passw0rd!"
<<<<<<< HEAD
PAUSE = 4  # seconds to read each step in the video
=======
PAUSE = 5  # seconds to read each step in the video
>>>>>>> origin/main


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request) as response:
            status, kind, text = response.status, response.headers.get("Content-Type", ""), response.read().decode()
    except urllib.error.HTTPError as error:
        status, kind, text = error.code, error.headers.get("Content-Type", ""), error.read().decode()
    except urllib.error.URLError:
        sys.exit("Cannot reach the server. Start it first with: python manage.py runserver")
    if "json" in kind and text:
        return status, json.loads(text)
    return status, text


def step(title, method, path, body=None, token=None):
    print(f"\n=== {title}")
    print(f"{method} /api/v1{path}")
    status, result = call(method, path, body, token)
    print(f"-> {status}")
    if isinstance(result, (dict, list)):
        shown = dict(result) if isinstance(result, dict) else result
        if isinstance(shown, dict) and "token" in shown:
            shown["token"] = shown["token"][:20] + "..."
        print(json.dumps(shown, indent=2))
    else:
        print(result)
    time.sleep(PAUSE)
    return status, result


def login(email):
    _, result = call("POST", "/auth/login/", {"email": email, "password": PASSWORD})
    return result["token"]


today = time.strftime("%Y-%m-%d")
month_start = time.strftime("%Y-%m-01")

print("SmartSpend - Team H5 - Sprint 2 demo")
call("POST", "/auth/register/", {"email": EMAIL, "password": PASSWORD})
token = login(EMAIL)
print(f"\nLogged in as {EMAIL}")
_, food = call("POST", "/categories/", {"name": "Food"}, token)
_, budget = step("1. Monthly Food budget of 1000", "POST", "/budgets/",
                 {"category": food["id"], "period": "MONTHLY", "limit_amount": "1000.00", "start_date": month_start}, token)
for amount in ("300.00", "250.00", "300.00"):
    call("POST", "/expenses/", {"category": food["id"], "amount": amount, "expense_date": today}, token)
step("2. Spent 850 of 1000: the 80% alert appears (FR-013, FR-015)", "GET", "/alerts/", token=token)
step("3. One more expense of 200 takes it over the limit", "POST", "/expenses/",
     {"category": food["id"], "amount": "200.00", "expense_date": today, "note": "dinner"}, token)
_, alerts = step("4. A second, separate 'Budget exceeded' alert (FR-014)", "GET", "/alerts/", token=token)
step("5. Acknowledge one alert (FR-015)", "POST", f"/alerts/{alerts[0]['id']}/acknowledge/", token=token)
step("6. It no longer shows as active", "GET", "/alerts/", token=token)
step("7. Budget shows spent and remaining (FR-011)", "GET", f"/budgets/{budget['id']}/", token=token)
step("8. Weekly spend trend for a chart (FR-017)", "GET", f"/analytics/trend/?from={month_start}&to={today}&granularity=weekly", token=token)
step("9. Export this month as CSV (FR-018)", "GET", f"/reports/export/?from={month_start}&to={today}", token=token)
step("10. HTML in a note is rejected (SEC-003)", "POST", "/expenses/",
     {"category": food["id"], "amount": "10.00", "expense_date": today, "note": "<script>alert(1)</script>"}, token)
step("11. My profile: no password or hash in the response (SEC-006)", "GET", "/auth/me/", token=token)
step("12. A normal user cannot open admin analytics (FR-021)", "GET", "/admin/analytics/", token=token)

call("POST", "/auth/register/", {"email": ADMIN_EMAIL, "password": PASSWORD})
subprocess.run(
    [sys.executable, "manage.py", "shell", "-c",
     f"from accounts.models import User; User.objects.filter(email='{ADMIN_EMAIL}').update(role='ADMIN')"],
    cwd=REPO, check=True,
)
admin_token = login(ADMIN_EMAIL)
print(f"\nLogged in as administrator {ADMIN_EMAIL}")
_, utilities = step("13. Admin adds a master category (FR-019)", "POST", "/admin/categories/", {"name": f"Utilities {RUN}"}, admin_token)
step("14. Admin disables it; old expenses stay intact (FR-019)", "PATCH", f"/admin/categories/{utilities['id']}/", {"is_active": False}, admin_token)
step("15. Admin sees anonymised usage totals (FR-020)", "GET", "/admin/analytics/", token=admin_token)
print("\nDemo complete.")
