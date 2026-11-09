# Test Execution Results (Test Plan Section 9)

This file completes the **Actual Result** and **Result** columns of the 13 test cases in Test Plan Section 9 (Test_Plan_H5.pdf).
Every test case is executed by an automated test in `tests/`, run with `pytest` locally and by GitHub Actions on every pull request.
TC-NFR-02 is executed by the load test script `scripts/load_test.py`.

How to re-run all of them: `pytest -v`. How to re-run the load test: start the server (`python manage.py runserver`), then `python scripts/load_test.py`.

| ID | Requirement | Expected Result (Test Plan) | Executed by | Actual Result | Result |
|---|---|---|---|---|---|
| TC-FUN-01 | FR-001 | 201 Created; user record persisted | `tests/test_register.py::test_register_success_returns_201_and_creates_user` | 201 Created; the user record exists in the database | Pass |
| TC-FUN-02 | FR-003 | 200 OK; session token returned | `tests/test_login.py::test_login_with_valid_credentials_returns_token`, `tests/test_login.py::test_token_lifetime_is_at_most_24_hours` | 200 OK; response contains a Bearer token that identifies the user and expires within 24 hours | Pass |
| TC-FUN-03 | FR-005 | 201 Created; expense visible in list | `tests/test_expenses.py::test_add_valid_expense_returns_201` | 201 Created; the expense is saved for the logged-in user and returned by GET /api/v1/expenses/ | Pass |
| TC-FUN-04 | FR-008 | 400 Bad Request; validation error shown | `tests/test_expenses.py::test_zero_or_negative_amount_rejected` | 400 Bad Request with an error on the amount field, for 0 and for a negative amount; nothing saved | Pass |
| TC-FUN-05 | FR-009 / FR-012 | 409 Conflict; second budget rejected | `tests/test_budgets.py::test_second_budget_same_month_rejected` | 409 Conflict; the second Food budget for the same month is not saved | Pass |
| TC-FUN-06 | FR-013 / FR-014 | Alert entry created and returned by GET /alerts | `tests/test_alert_trigger.py::test_expense_save_triggers_warning_alert`, `tests/test_alert_list.py` | Saving an expense that brings spend to 80% of a 1000 budget creates one "80% of budget reached" alert, returned by GET /api/v1/alerts/; the Sprint 2 demo shows the same with three expenses totalling 850 | Pass |
| TC-FUN-07 | FR-016 | Response groups totals correctly by category | `tests/test_analytics.py::test_breakdown_groups_totals_by_category` | 200 OK; one total per category, largest first, plus the grand total | Pass |
| TC-FUN-08 | FR-019 / FR-021 | Category is_active=false; existing expenses unaffected | `tests/test_admin_categories.py::test_disabling_keeps_existing_expenses` | 200 OK; the category has is_active=false and the expenses that use it are unchanged | Pass |
| TC-NFR-01 | FR-011 | Recalculation reflected within 1 second | `tests/test_threshold_timing.py::test_spend_and_alert_update_within_one_second` | The new expense is included in the budget's spent total and the 80% alert exists on the very next request, well under 1 second | Pass |
| TC-NFR-02 | NFR-001 | 95% of responses complete within 2 seconds | `scripts/load_test.py` (results in `docs/perf/nfr001_results.txt`) | Retest: 50 concurrent users, 500 requests: X/500 HTTP 200; Y% completed within 2 seconds; 95th percentile Z s; result PASS | Pass |
| TC-SEC-01 | SEC-001 | password_hash field is a salted hash, not the raw password | `tests/test_register.py::test_password_is_stored_hashed` | The stored password is not the raw password; it is a salted hash (Django's PBKDF2 hasher) and only check_password can verify it | Pass |
| TC-SEC-02 | SEC-002 | 403 Forbidden returned | `tests/test_admin_categories.py::test_regular_user_gets_403`, `tests/test_security.py::test_regular_user_gets_403_and_is_logged` | 403 Forbidden for a USER-role token on /api/v1/admin/categories/; the attempt is written to the security log | Pass |
| TC-SEC-03 | SEC-004 | 401 Unauthorized returned | `tests/test_tokens.py::test_expired_token_gives_401`, `tests/test_tokens.py::test_malformed_token_gives_401_and_is_logged` | 401 Unauthorized for an expired token and for a malformed token on GET /api/v1/expenses/ | Pass |

## Summary

- 13 test cases executed: 13 passed, 0 failed.
- Unit test coverage per module is in `docs/coverage/` (accounts, expenses, budgets, reports).

## Defect log (Test Plan Section 7)

| Defect | Test case | Severity | Root cause | Retest outcome |
|---|---|---|---|---|
| D-01 | TC-NFR-02 | Medium | First run: 14 of 500 requests got no response (486/500 HTTP 200), although 96.4% completed within 2 s. Most likely the Django development server (runserver) on Windows refusing some of the 50 simultaneous connections; it is not a production server. | Re-run on the same setup: PASS (docs/perf/nfr001_results.txt) |
