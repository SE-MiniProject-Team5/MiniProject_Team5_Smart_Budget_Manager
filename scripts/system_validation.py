"""System validation (Test Plan Section 4 level 3 and Section 5.1): runs against the live server.

1. Start the server in another window:   python manage.py runserver
2. Run, from the repo folder:            python scripts/system_validation.py --out docs/reports/system_validation_run.txt

It checks one end-to-end user journey and every row of the Test Plan 5.1 security validation table
through the real HTTP API (like a Postman collection), then prints PASS or FAIL for each check.
Uses only the Python standard library, plus the project's Django settings (security log path and signing secret).
"""
import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
REPO = pathlib.Path(__file__).resolve().parents[1]  # the folder with manage.py
PASSWORD = "Passw0rd!"
RUN = uuid.uuid4().hex[:6]
results = []  # (section, check, passed, detail)


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status, text = response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        status, text = error.code, error.read().decode()
    try:
        return status, json.loads(text) if text else None, text
    except ValueError:
        return status, None, text


def check(section, name, passed, detail):
    results.append((section, name, bool(passed), detail))


def new_user(label):
    email = f"{label}-{RUN}@smartspend.test"
    call("POST", "/auth/register/", {"email": email, "password": PASSWORD})
    _, body, _ = call("POST", "/auth/login/", {"email": email, "password": PASSWORD})
    return email, body["token"]


def django_settings():
    sys.path.insert(0, str(REPO))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartspend.settings")
    import django
    from django.conf import settings

    django.setup()
    return settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="also write the results to this file")
    args = parser.parse_args()
    try:
        call("GET", "/health/")
    except urllib.error.URLError:
        sys.exit("Cannot reach the server. Start it first with: python manage.py runserver")
    settings = django_settings()
    log_file = pathlib.Path(settings.LOGGING["handlers"]["security_file"]["filename"])
    today = time.strftime("%Y-%m-%d")
    month_start = time.strftime("%Y-%m-01")

    # ---- End-to-end journey: register -> add expense -> receive alert (Test Plan Section 4, level 3) ----
    owner_email, owner = new_user("owner")
    _, food, _ = call("POST", "/categories/", {"name": "Food"}, owner)
    status, budget, _ = call("POST", "/budgets/", {"category": food["id"], "period": "MONTHLY", "limit_amount": "1000.00", "start_date": month_start}, owner)
    check("Journey", "Create a 1000 monthly budget", status == 201, f"HTTP {status}")
    expense_ids = []
    for amount in ("300.00", "250.00", "300.00"):
        status, expense, _ = call("POST", "/expenses/", {"category": food["id"], "amount": amount, "expense_date": today}, owner)
        expense_ids.append(expense["id"])
    check("Journey", "Add three expenses totalling 850", status == 201 and len(expense_ids) == 3, f"HTTP {status}")
    status, alerts, _ = call("GET", "/alerts/", token=owner)
    check("Journey", "80% alert is listed by GET /alerts/", status == 200 and [a["threshold_type"] for a in alerts] == ["80"], f"HTTP {status}, alerts {[a['threshold_type'] for a in alerts]}")
    status, body, _ = call("GET", f"/budgets/{budget['id']}/", token=owner)
    check("Journey", "Budget shows spent 850.00 and remaining 150.00", body.get("spent") == "850.00" and body.get("remaining") == "150.00", f"spent {body.get('spent')}, remaining {body.get('remaining')}")
    status, _, _ = call("POST", f"/alerts/{alerts[0]['id']}/acknowledge/", token=owner)
    _, after, _ = call("GET", "/alerts/", token=owner)
    check("Journey", "Acknowledged alert leaves the active list", status == 200 and after == [], f"HTTP {status}, active after: {len(after)}")

    # ---- 5.1 Confidentiality: cross-user access is rejected with 403 ----
    _, other = new_user("other")
    for method, path in (("GET", f"/expenses/{expense_ids[0]}/"), ("PATCH", f"/expenses/{expense_ids[0]}/"),
                         ("DELETE", f"/expenses/{expense_ids[0]}/"), ("GET", f"/budgets/{budget['id']}/"),
                         ("PATCH", f"/budgets/{budget['id']}/"), ("DELETE", f"/budgets/{budget['id']}/")):
        body = {"note": "changed"} if method == "PATCH" and "expenses" in path else ({"limit_amount": "1.00"} if method == "PATCH" else None)
        status, _, _ = call(method, path, body, other)
        check("5.1 Confidentiality", f"Another user's {method} {path.split('/')[1]}/<id>/ is rejected", status == 403, f"HTTP {status} (expected 403)")
    _, still, _ = call("GET", f"/budgets/{budget['id']}/", token=owner)
    check("5.1 Confidentiality", "Owner's budget unchanged after those attempts", still.get("limit_amount") == "1000.00", f"limit {still.get('limit_amount')}")

    # ---- 5.1 Confidentiality: no hash, raw password or signing secret in any response ----
    texts = [call("POST", "/auth/register/", {"email": f"leak-{RUN}@smartspend.test", "password": PASSWORD})[2],
             call("POST", "/auth/login/", {"email": owner_email, "password": PASSWORD})[2],
             call("GET", "/auth/me/", token=owner)[2], call("GET", "/expenses/", token=owner)[2],
             call("GET", "/budgets/", token=owner)[2], call("GET", "/alerts/", token=owner)[2],
             call("POST", "/auth/login/", {"email": owner_email, "password": "wrong"})[2]]
    leaks = [w for w in ("pbkdf2_", PASSWORD, settings.SECRET_KEY, '"password"') if any(w in t for t in texts)]
    check("5.1 Confidentiality", "No response contains a password hash, the raw password or the signing secret", not leaks, f"{len(texts)} responses checked, leaks: {leaks or 'none'}")

    # ---- 5.1 Integrity: invalid data is rejected server-side, bypassing any UI ----
    status, _, _ = call("POST", "/expenses/", {"category": food["id"], "amount": "0.00", "expense_date": today}, owner)
    check("5.1 Integrity", "Expense amount 0 rejected", status == 400, f"HTTP {status} (expected 400)")
    status, _, _ = call("POST", "/expenses/", {"category": food["id"], "amount": "-50.00", "expense_date": today}, owner)
    check("5.1 Integrity", "Negative expense amount rejected", status == 400, f"HTTP {status} (expected 400)")
    status, _, _ = call("POST", "/budgets/", {"category": food["id"], "period": "MONTHLY", "limit_amount": "500.00", "start_date": month_start}, owner)
    check("5.1 Integrity", "Overlapping budget period rejected", status == 409, f"HTTP {status} (expected 409)")

    # ---- 5.1 Integrity: every Admin endpoint rejects a User-role token with 403 ----
    for method, path, body in (("GET", "/admin/categories/", None), ("POST", "/admin/categories/", {"name": f"X {RUN}"}),
                               ("PATCH", f"/admin/categories/{food['id']}/", {"is_active": False}), ("GET", "/admin/analytics/", None)):
        status, _, _ = call(method, path, body, owner)
        check("5.1 Integrity", f"User token on {method} {path.replace(food['id'], '<id>')} rejected", status == 403, f"HTTP {status} (expected 403)")

    # ---- 5.1 Accountability: 3 failed logins + 1 unauthorized admin call are logged ----
    target = f"target-{RUN}@smartspend.test"
    call("POST", "/auth/register/", {"email": target, "password": PASSWORD})
    for attempt in range(3):
        call("POST", "/auth/login/", {"email": target, "password": f"Wrong-{attempt}-pass"})
    _, target_login, _ = call("POST", "/auth/login/", {"email": target, "password": PASSWORD})
    call("GET", "/admin/analytics/", token=target_login["token"])
    time.sleep(0.5)
    lines = [line for line in log_file.read_text(encoding="utf-8", errors="replace").splitlines() if target in line]
    failed = [line for line in lines if "event=failed_login" in line]
    admin = [line for line in lines if "event=unauthorized_admin_access" in line]
    dated = all(line[:4].isdigit() and line[4] == "-" for line in lines)
    check("5.1 Accountability", "3 failed logins logged with timestamp and account", len(failed) == 3 and dated, f"{len(failed)} failed_login lines for {target}")
    check("5.1 Accountability", "Unauthorized admin call logged with timestamp and account", len(admin) == 1 and dated, f"{len(admin)} unauthorized_admin_access line(s)")
    whole_log = log_file.read_text(encoding="utf-8", errors="replace")
    check("5.1 Accountability", "No password appears anywhere in the security log", PASSWORD not in whole_log and "Wrong-0-pass" not in whole_log, f"checked {log_file.name}")

    passed = sum(1 for r in results if r[2])
    lines = ["SmartSpend system validation (Test Plan Section 4 system testing and Section 5.1 security validation)",
             f"Server: {BASE}", ""]
    for section, name, ok, detail in results:
        lines.append(f"[{'PASS' if ok else 'FAIL'}] {section}: {name} ({detail})")
    lines += ["", f"Checks passed: {passed}/{len(results)}", f"Result: {'PASS' if passed == len(results) else 'FAIL'}"]
    report = "\n".join(lines)
    print(report)
    if args.out:
        pathlib.Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"Saved to {args.out}")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
