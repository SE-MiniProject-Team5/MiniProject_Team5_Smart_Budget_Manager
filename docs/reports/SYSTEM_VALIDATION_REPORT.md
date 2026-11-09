# System Validation Report

SmartSpend (Team H5), v1.0. Course Part-3, item 2b-ii.

This report validates the delivered system against the SRS (SRS_H5.pdf) following the Test Plan (Test_Plan_H5.pdf): every requirement, the Section 5.1 security validation gate, and complete user journeys run against the live system.

## 1. Scope and approach

The Test Plan (Section 4) tests bottom-up at four levels. Each level, and the evidence for it:

| Level (Test Plan Section 4) | How it was done | Evidence |
|---|---|---|
| 1. Unit testing | pytest tests that call each service function, serializer and rule directly | [UNIT_TEST_REPORT.md](UNIT_TEST_REPORT.md) |
| 2. Integration testing | pytest tests that call every API endpoint through Django REST Framework's test client, with a real test database | [UNIT_TEST_REPORT.md](UNIT_TEST_REPORT.md) (API level) |
| 3. System testing | `scripts/system_validation.py` drives the running server over real HTTP, like a Postman collection; the two demo scripts walk through every user-facing feature | [system_validation_run.txt](system_validation_run.txt), `docs/demo/` |
| 4. Security testing | The Section 5.1 table, checked both by automated tests and live by `scripts/system_validation.py` | Section 4 below |

Black-box validation (levels 3 and 4) checks behaviour only through the API, without looking at the code. White-box validation (levels 1 and 2) is measured by line and branch coverage: [CODE_COVERAGE_REPORT.md](CODE_COVERAGE_REPORT.md) and [BRANCH_COVERAGE_REPORT.md](BRANCH_COVERAGE_REPORT.md).

**Environment:** the application running with `python manage.py runserver` on a team member's Windows machine, with SQLite (DEVIATIONS #6); the same tests run in GitHub Actions on every pull request and every push to `main`.

## 2. Requirement validation

| Requirement | What must hold | Validated by | Result |
|---|---|---|---|
| FR-001 | A user can register | TC-FUN-01; system journey (each run registers new users) | Pass |
| FR-002 | A duplicate email is rejected | `tests/test_register.py`, `tests/test_auth_units.py` | Pass |
| FR-003 | A user can log in | TC-FUN-02; system journey | Pass |
| FR-004 | The session token lasts at most 24 hours | TC-FUN-02, TC-SEC-03 | Pass |
| FR-005 | A user can add an expense | TC-FUN-03; system journey | Pass |
| FR-006 | A user can edit or delete only their own expenses | `tests/test_expense_edit.py`; Section 4, cross-user checks | Pass |
| FR-007 | Predefined and custom categories (name up to 50 characters) | `tests/test_categories.py`, `tests/test_expense_api_rules.py` | Pass |
| FR-008 | An amount of 0 or less is rejected | TC-FUN-04; Section 4, Integrity | Pass |
| FR-009 | A user can create a weekly or monthly budget | TC-FUN-05; system journey | Pass |
| FR-010 | A user can edit their own budget | `tests/test_budget_edit.py` | Pass |
| FR-011 | Spent and remaining are always up to date | TC-NFR-01; system journey (spent 850.00, remaining 150.00) | Pass |
| FR-012 | Overlapping budgets are rejected | TC-FUN-05; Section 4, Integrity (409) | Pass |
| FR-013 | Alert at 80% of a budget | TC-FUN-06; system journey | Pass |
| FR-014 | A second, distinct alert above 100% | TC-FUN-09; Sprint 2 demo step 4 | Pass |
| FR-015 | Active alerts listed and can be acknowledged | TC-FUN-10; system journey | Pass |
| FR-016 | Spend by category for a date range | TC-FUN-07; Sprint 1 demo | Pass |
| FR-017 | Daily or weekly spend trend | TC-FUN-11; Sprint 2 demo step 8 | Pass |
| FR-018 | CSV export for a chosen period | TC-FUN-12; Sprint 2 demo step 9 | Pass |
| FR-019 | Admin adds, edits and disables master categories | TC-FUN-08; Sprint 2 demo steps 13 and 14 | Pass |
| FR-020 | Admin sees anonymised usage totals | TC-FUN-13; Sprint 2 demo step 15 | Pass |
| FR-021 | Admin features only for admins | TC-SEC-02, TC-FUN-13; Section 4, Integrity | Pass |
| NFR-001 | 95% of dashboard requests within 2 s at 50 concurrent users | TC-NFR-02, `scripts/load_test.py`, `docs/perf/nfr001_results.txt` | See [TEST_RESULTS.md](../TEST_RESULTS.md), TC-NFR-02 and defect D-01 |
| NFR-002 | Threshold recalculation within 1 s | TC-NFR-01 | Pass |
| SEC-001 | Passwords stored only as salted hashes | TC-SEC-01 | Pass |
| SEC-002 | Role-based access control | TC-SEC-02; Section 4, Integrity | Pass |
| SEC-003 | All input validated server-side | TC-SEC-04; Section 4, Integrity | Pass |
| SEC-004 | Invalid or expired token gives 401 | TC-SEC-03 | Pass |
| SEC-005 | Security events logged | TC-SEC-06; Section 4, Accountability | Pass |
| SEC-006 | No sensitive fields in responses | TC-SEC-05; Section 4, Confidentiality | Pass |

Test case IDs refer to the updated test case document, [TEST_CASES.md](../TEST_CASES.md); their execution results are in [TEST_RESULTS.md](../TEST_RESULTS.md) (TC-FUN-01 to TC-SEC-03) and TEST_CASES.md Part B (TC-FUN-09 onwards).

## 3. System test: end-to-end user journey

The Test Plan's example journey, "register, add expense, receive alert", was run against the live server by `scripts/system_validation.py`. Results from [system_validation_run.txt](system_validation_run.txt):

| Step | Expected | Result |
|---|---|---|
| Register and log in a new user; create a monthly budget of 1000 | 201 Created | Pass |
| Add three expenses totalling 850 | 201 Created each | Pass |
| `GET /api/v1/alerts/` | Exactly one 80% alert | Pass |
| `GET /api/v1/budgets/<id>/` | spent 850.00, remaining 150.00 | Pass |
| Acknowledge the alert, list again | The alert is no longer active | Pass |

The two recorded demos (`docs/demo/sprint1_demo.mp4`, `docs/demo/sprint2_demo.mp4`) show the remaining user journeys on the working product: categories, budgets with overlap rejection and analytics in Sprint 1; exceeded alerts, trend, CSV export, input rejection, profile, and the admin journey in Sprint 2.

## 4. Security validation (Test Plan Section 5.1)

Section 5.1 is a separate pass/fail gate. Each row was validated live against the running server by `scripts/system_validation.py`, and by the automated tests listed.

| Security objective | Validation activity (Test Plan) | Pass criterion | Live result | Automated tests | Result |
|---|---|---|---|---|---|
| Confidentiality | Access another user's expenses and budgets with a valid token of a different user | 403 for every cross-user attempt | GET, PATCH and DELETE on another user's expense and budget: 403 each (6 of 6); the owner's budget unchanged | `tests/test_expense_edit.py`, `tests/test_budget_edit.py` | Pass |
| Confidentiality | Inspect API responses for a password hash or the token signing secret | No response contains either | 7 responses checked (register, login, failed login, profile, expenses, budgets, alerts): no hash, password or secret | `tests/test_no_sensitive_fields.py`, `tests/test_me.py` | Pass |
| Integrity | Submit a zero and a negative amount, and an overlapping budget, directly to the API | Rejected server-side (400/409) | Amount 0: 400. Amount -50: 400. Overlapping budget: 409 | `tests/test_expenses.py`, `tests/test_budgets.py` | Pass |
| Integrity | Call Admin-only endpoints with a valid User-role token | 403 for every Admin endpoint tested | GET and POST /admin/categories/, PATCH /admin/categories/<id>/, GET /admin/analytics/: 403 each (4 of 4) | `tests/test_admin_categories.py`, `tests/test_admin_analytics.py`, `tests/test_security.py` | Pass |
| Accountability | Trigger 3 failed logins and 1 unauthorized admin call; inspect the security log | All 4 events logged with timestamp and account; no password in any log entry | 3 `failed_login` and 1 `unauthorized_admin_access` lines for the test account, each with timestamp, account and endpoint; no password anywhere in `logs/security.log` | `tests/test_login.py`, `tests/test_security.py` | Pass |

Security validation gate: **passed**. Every row meets its pass criterion.

## 5. Defects and deviations

- **Defects:** the only defect found during validation is D-01 (TC-NFR-02, load test), recorded with severity, root cause and retest outcome in [TEST_RESULTS.md](../TEST_RESULTS.md).
- **Deviations:** every place where the system differs from the SRS, SAD or Test Plan is listed with its reason in [DEVIATIONS.md](../../DEVIATIONS.md) and [DESIGN_UPDATES.md](../DESIGN_UPDATES.md). None of them removes a requirement; they change how a requirement is met (for example, extra endpoints, or the token format).

## 6. Conclusion

Against the Test Plan's exit criteria (Section 4) and pass/fail criteria (Section 5):

- Every functional requirement FR-001 to FR-021 and every security requirement SEC-001 to SEC-006 is validated and passes.
- NFR-002 passes. NFR-001's result and retest are recorded under defect D-01.
- The Section 5.1 security validation gate passes on every row.
- Each module's line coverage is above the 70% target (see the coverage reports).

SmartSpend v1.0 meets its SRS requirements as listed above and is validated for the final demonstration.
