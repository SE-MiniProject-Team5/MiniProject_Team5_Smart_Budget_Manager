# Test Case Document (updated after Sprint 1 and Sprint 2)

SmartSpend (Team H5). This updates Test Plan Section 9 (Test_Plan_H5.pdf) to match the delivered v1.0 system, as required by the course Part-3 brief (item 1: update the test cases based on the changes made during the sprints).

- **Part A** is the original 13 test cases, corrected where the sprints changed an endpoint, a method or the test data. Each row says what changed and why. Their execution results are in [TEST_RESULTS.md](TEST_RESULTS.md).
- **Part B** adds test cases for features delivered in Sprint 2 that the original 13 did not cover.

General changes that apply to every case:

- All endpoints are under `/api/v1/` and end with a slash, for example `/api/v1/auth/register/` (DEVIATIONS #7).
- "Logged in" means the request sends `Authorization: Bearer <token>`, where the token comes from `POST /api/v1/auth/login/` (DEVIATIONS #8).
- Test cases are executed by automated tests (pytest) against a fresh test database, and in CI on every pull request (DEVIATIONS #1, #6). The automated test that executes each case is named in the table.

## Part A: original test cases, updated

| ID | Module | Description | Precondition | Steps | Test Data | Expected Result | Executed by | Change from Test Plan |
|---|---|---|---|---|---|---|---|---|
| TC-FUN-01 | Auth | Register with a new, unique email | Server running, no user with this email | 1. `POST /api/v1/auth/register/` 2. Check the user exists | email=a@test.com, password=Passw0rd! | 201 Created; user record saved; response has only id, email, role | `tests/test_register.py::test_register_success_returns_201_and_creates_user` | Exact endpoint path; response fields restricted by SEC-006 |
| TC-FUN-02 | Auth | Login with valid credentials | User registered | 1. `POST /api/v1/auth/login/` 2. Inspect response | email=a@test.com, password=Passw0rd! | 200 OK; Bearer token returned, valid for at most 24 hours | `tests/test_login.py::test_login_with_valid_credentials_returns_token` | Token is a signed Django token, not a JWT (DEVIATIONS #8) |
| TC-FUN-03 | Expense | Add a valid expense | Logged in; category exists | 1. `POST /api/v1/expenses/` 2. `GET /api/v1/expenses/` | amount=250.00, category=Food, expense_date=today | 201 Created; expense appears in the user's list | `tests/test_expenses.py::test_add_valid_expense_returns_201` | Exact endpoint path; amount sent as a decimal string |
| TC-FUN-04 | Expense | Reject zero or negative amount | Logged in | 1. `POST /api/v1/expenses/` with amount 0, then -5 | amount=0 and amount=-5, category=Food | 400 Bad Request with an error on `amount`; nothing saved | `tests/test_expenses.py::test_zero_or_negative_amount_rejected` | Negative amount added (FR-008 says greater than 0) |
| TC-FUN-05 | Budget | Reject overlapping budget for the same category and period | An active Food budget exists for this month | 1. `POST /api/v1/budgets/` for Food, same month | category=Food, period=MONTHLY, start_date=first of month | 409 Conflict; second budget not saved | `tests/test_budgets.py::test_second_budget_same_month_rejected` | Exact endpoint path |
| TC-FUN-06 | Alert | Generate alert at 80% threshold | Food budget of 1000, no prior spend | 1. Add expense(s) reaching 80% or more 2. `GET /api/v1/alerts/` | One expense of 800, or three summing to 850 | One "80% of budget reached" alert created and returned by GET /api/v1/alerts/ | `tests/test_alert_trigger.py::test_expense_save_triggers_warning_alert`, `tests/test_alert_list.py` | Alerts are created automatically when an expense is saved (DEVIATIONS #14) |
| TC-FUN-07 | Analytics | Category-wise spend breakdown | User has expenses in 2 or more categories | 1. `GET /api/v1/analytics/?from=<first of month>&to=<today>` | Current month | 200 OK; one total per category, largest first, plus the grand total | `tests/test_analytics.py::test_breakdown_groups_totals_by_category` | Trend data moved to its own endpoint (DEVIATIONS #9); this case covers the breakdown only |
| TC-FUN-08 | Admin | Admin disables a category | Logged in as Admin; master category exists | 1. `PATCH /api/v1/admin/categories/<id>/` 2. Check the category and its expenses | is_active=false | 200 OK; category is_active=false; existing expenses unchanged | `tests/test_admin_categories.py::test_disabling_keeps_existing_expenses` | Disable is a PATCH on the category's own URL, not a POST (DEVIATIONS #10) |
| TC-NFR-01 | Budget | Threshold recalculation within 1 s | Active budget exists | 1. Add an expense 2. Measure time until the budget and alerts show it | 1 expense, amount=100 | Spent total and 80% alert updated in under 1 second | `tests/test_threshold_timing.py::test_spend_and_alert_update_within_one_second` | Automated test added in Sprint 2 (before, no test measured the time) |
| TC-NFR-02 | Full stack | Dashboard responds within 2 s under load | Server running | 1. Run `python scripts/load_test.py` | 50 concurrent users x 10 requests to GET /api/v1/analytics/ | 95% of responses within 2 seconds | `scripts/load_test.py` (results in `docs/perf/nfr001_results.txt`) | Load tool is a Python script instead of a separate tool |
| TC-SEC-01 | Auth | Password never stored in plaintext | New user registered | 1. Read the user record from the database | n/a | Stored password is a salted hash, never the raw password | `tests/test_register.py::test_password_is_stored_hashed` | Hash is in Django's `password` field (DEVIATIONS #5) |
| TC-SEC-02 | Admin API | User role blocked from Admin endpoint | Logged in as a regular User | 1. `POST /api/v1/admin/categories/` with the User token | User-role token | 403 Forbidden; the attempt is logged | `tests/test_admin_categories.py::test_regular_user_gets_403`, `tests/test_security.py::test_regular_user_gets_403_and_is_logged` | Exact endpoint path; logging check added (SEC-005) |
| TC-SEC-03 | Auth | Expired token rejected on protected endpoint | A token older than 24 hours | 1. `GET /api/v1/expenses/` with that token | Expired token; also a malformed token | 401 Unauthorized; the attempt is logged | `tests/test_tokens.py::test_expired_token_gives_401`, `tests/test_tokens.py::test_malformed_token_gives_401_and_is_logged` | Malformed token case added |

## Part B: new test cases for Sprint 2 features

All of these were executed by the named automated tests in the final `pytest` run (see [reports/UNIT_TEST_REPORT.md](reports/UNIT_TEST_REPORT.md)).

| ID | Module | Requirement | Description | Precondition | Steps | Test Data | Expected Result | Executed by | Actual Result | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-FUN-09 | Alert | FR-014 | Second, distinct alert when the budget is exceeded | Food budget of 1000 | 1. Add an expense taking spend above 1000 2. Check alerts | One expense of 1100 | Both a "80% of budget reached" and a "Budget exceeded" alert exist | `tests/test_alert_trigger.py::test_expense_save_triggers_exceeded_alert` | Both alerts created | Pass |
| TC-FUN-10 | Alert | FR-015 | Acknowledge an alert | User has one active alert | 1. `POST /api/v1/alerts/<id>/acknowledge/` 2. `GET /api/v1/alerts/` | The alert's id | 200 OK; the alert no longer appears in the active list; another user's alert id gives 404 | `tests/test_alert_acknowledge.py::test_acknowledge_hides_alert`, `tests/test_alert_acknowledge.py::test_cannot_acknowledge_someone_elses_alert` | Alert hidden after acknowledging; another user's alert gives 404 | Pass |
| TC-FUN-11 | Analytics | FR-017 | Weekly spend trend | User has expenses on different days | 1. `GET /api/v1/analytics/trend/?from=&to=&granularity=weekly` | A range covering two weeks | 200 OK; one total per week, weeks starting on Monday, 0.00 for weeks with no spend | `tests/test_trend.py::test_weekly_trend_groups_by_monday`, `tests/test_trend.py::test_daily_trend_lists_every_day_with_zeros` | Totals grouped by week from Monday; empty days and weeks show 0.00 | Pass |
| TC-FUN-12 | Report | FR-018 | CSV export of expenses for a period | User has expenses inside and outside the range | 1. `GET /api/v1/reports/export/?from=&to=` | One month | 200 OK; `text/csv` file of only this user's expenses in the range, oldest first; cells starting with = + - @ are escaped | `tests/test_export.py::test_export_returns_csv_of_own_expenses_in_range`, `tests/test_export.py::test_formula_like_text_is_neutralised` | CSV has only the user's in-range expenses; formula-like text starts with ' | Pass |
| TC-FUN-13 | Admin | FR-020, FR-021 | Anonymised usage totals for admins | Logged in as Admin | 1. `GET /api/v1/admin/analytics/` as Admin 2. Same call as a User | Admin token, then User token | Admin: 200 OK with counts only, no emails, names or per-user amounts. User: 403 | `tests/test_admin_analytics.py::test_admin_sees_totals_only`, `tests/test_admin_analytics.py::test_regular_user_gets_403` | Admin sees totals only; User gets 403 | Pass |
| TC-SEC-04 | Expense | SEC-003 | Unsafe input rejected server-side | Logged in | 1. `POST /api/v1/expenses/` with HTML in the note 2. With control characters 3. With malformed values | note=`<script>alert(1)</script>`, a note with a tab, amount=abc | 400 Bad Request each time; nothing saved | `tests/test_input_validation.py::test_html_in_note_rejected`, `tests/test_input_validation.py::test_control_characters_in_note_rejected`, `tests/test_input_validation.py::test_malformed_values_rejected` | 400 for each; no record saved | Pass |
| TC-SEC-05 | Auth | SEC-006 | No sensitive fields in responses | Logged in | 1. `GET /api/v1/auth/me/` 2. Call every endpoint and search the responses | n/a | Only id, email, role returned; no response contains a password hash, the raw password or the signing secret | `tests/test_me.py::test_me_returns_only_safe_fields`, `tests/test_no_sensitive_fields.py::test_no_endpoint_leaks_secrets` | Only safe fields returned; no secret found in any response | Pass |
| TC-SEC-06 | Auth, Admin | SEC-005 | Security events are logged | Server running | 1. Log in with a wrong password 2. Call an Admin endpoint as a User 3. Read the security log | Wrong password; User token | Each event is logged with a timestamp, the account and the endpoint; no password in the log | `tests/test_login.py::test_wrong_password_gives_401_and_is_logged`, `tests/test_security.py::test_log_entry_has_timestamp_account_and_endpoint` | Both events logged with timestamp, account and endpoint | Pass |

## Coverage of requirements by test cases

| Requirement area | Test cases |
|---|---|
| Auth (FR-001 to FR-004) | TC-FUN-01, TC-FUN-02, TC-SEC-03 |
| Expenses (FR-005 to FR-008) | TC-FUN-03, TC-FUN-04 |
| Budgets (FR-009 to FR-012) | TC-FUN-05, TC-NFR-01 |
| Alerts (FR-013 to FR-015) | TC-FUN-06, TC-FUN-09, TC-FUN-10 |
| Reports (FR-016 to FR-018) | TC-FUN-07, TC-FUN-11, TC-FUN-12 |
| Admin (FR-019 to FR-021) | TC-FUN-08, TC-FUN-13, TC-SEC-02 |
| Non-functional (NFR-001, NFR-002) | TC-NFR-02, TC-NFR-01 |
| Security (SEC-001 to SEC-006) | TC-SEC-01 to TC-SEC-06 |

Requirements without their own test case here (for example FR-006, FR-007, FR-010) are covered by the automated unit and API tests listed in [reports/UNIT_TEST_REPORT.md](reports/UNIT_TEST_REPORT.md).
