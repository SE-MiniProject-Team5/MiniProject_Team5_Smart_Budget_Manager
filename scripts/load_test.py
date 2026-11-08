"""NFR-001 performance test: 95% of dashboard/analytics requests must answer within 2 seconds
with 50 concurrent users (Test Plan TC-NFR-02).

1. Start the server in another window:   python manage.py runserver
2. Run:                                     python scripts/load_test.py
   Save the results file as evidence:       python scripts/load_test.py --out docs/perf/nfr001_results.txt

It creates its own test user and sample expenses through the API, then sends
50 users x 10 requests to GET /api/v1/analytics/ at the same time. Standard library only.
"""
import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

BASE = "http://127.0.0.1:8000/api/v1"
USERS = 50  # concurrent users (NFR-001)
REQUESTS_PER_USER = 10
LIMIT_SECONDS = 2.0  # NFR-001: 95% of requests within 2 seconds


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, json.loads(response.read().decode() or "null")


def prepare():
    """Create a user, a category and 30 expenses, and return a login token."""
    email = f"load-{uuid.uuid4().hex[:8]}@smartspend.test"
    call("POST", "/auth/register/", {"email": email, "password": "Passw0rd!"})
    _, login = call("POST", "/auth/login/", {"email": email, "password": "Passw0rd!"})
    token = login["token"]
    _, category = call("POST", "/categories/", {"name": "Load test"}, token)
    for day in range(1, 31):
        call("POST", "/expenses/", {"category": category["id"], "amount": "10.00",
                                    "expense_date": f"2026-01-{day:02d}"}, token)
    return token


def one_user(token):
    """One simulated user: REQUESTS_PER_USER dashboard calls; returns each call's time in seconds."""
    times = []
    for _ in range(REQUESTS_PER_USER):
        started = time.perf_counter()
        try:
            status, _ = call("GET", "/analytics/?from=2026-01-01&to=2026-01-31", token=token)
        except (urllib.error.URLError, TimeoutError):
            status = 0
        times.append((time.perf_counter() - started, status))
    return times


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="also write the results to this file")
    args = parser.parse_args()
    try:
        token = prepare()
    except urllib.error.URLError:
        sys.exit("Cannot reach the server. Start it first with: python manage.py runserver")

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=USERS) as pool:
        results = [t for user_times in pool.map(one_user, [token] * USERS) for t in user_times]
    wall = time.perf_counter() - started

    times = sorted(t for t, _ in results)
    ok = sum(1 for _, status in results if status == 200)
    p95 = times[int(len(times) * 0.95) - 1]
    within = sum(1 for t in times if t <= LIMIT_SECONDS) / len(times) * 100
    verdict = "PASS" if within >= 95 and ok == len(results) else "FAIL"
    report = "\n".join([
        "NFR-001 load test (Test Plan TC-NFR-02)",
        "Endpoint: GET /api/v1/analytics/?from=2026-01-01&to=2026-01-31",
        f"Concurrent users: {USERS}, requests per user: {REQUESTS_PER_USER}, total: {len(results)}",
        f"Successful (HTTP 200): {ok}/{len(results)}",
        f"Median: {statistics.median(times):.3f} s   95th percentile: {p95:.3f} s   slowest: {times[-1]:.3f} s",
        f"Within {LIMIT_SECONDS:.0f} s: {within:.1f}% (required: 95%)",
        f"Total time: {wall:.1f} s",
        f"Result: {verdict}",
    ])
    print(report)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(report + "\n")
        print(f"Saved to {args.out}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
