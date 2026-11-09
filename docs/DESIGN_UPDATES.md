# Design Updates (SAD and SRS)

This file lists every change to endpoints, fields and components between the submitted documents
(SW_Architecture_Design_Spec_H5.pdf, SRS_H5.pdf) and the delivered v1.0 code, so that each can be explained at the final demo.
Rows that differ from the documents are also recorded, with the reason, in [DEVIATIONS.md](../DEVIATIONS.md) (the # column below points to that row).

## 1. API Design (SAD Section 8), as built

All paths are under `/api/v1/` and end with a slash (DEVIATIONS #7). Every endpoint except register, login and health needs `Authorization: Bearer <token>` (DEVIATIONS #8).

| Method | Endpoint | Purpose | Auth Required | Traces To | Change from SAD | DEVIATIONS # |
|---|---|---|---|---|---|---|
| POST | `/auth/register/` | Create a new user account | No | FR-001, FR-002 | Same | - |
| POST | `/auth/login/` | Authenticate and issue a session token | No | FR-003, FR-004 | Same | - |
| GET | `/auth/me/` | The caller's own profile (id, email, role only) | Yes (User) | SEC-006 | Added | 12 |
| GET, POST | `/categories/` | List usable categories; add a custom category | Yes (User) | FR-007 | Added | 12 |
| GET, POST | `/expenses/` | List own expenses; create an expense | Yes (User) | FR-005, FR-008 | GET added | 13 |
| GET, PUT, PATCH, DELETE | `/expenses/<id>/` | Read, update or delete an owned expense | Yes (User, owner) | FR-006 | GET, PATCH added | 13 |
| GET, POST | `/budgets/` | List own budgets; create a budget | Yes (User) | FR-009, FR-012 | GET added | 13 |
| GET, PUT, PATCH, DELETE | `/budgets/<id>/` | Read, update or delete an owned budget | Yes (User, owner) | FR-010, FR-011 | GET, PATCH, DELETE added | 13 |
| GET | `/alerts/` | Active (unacknowledged) alerts for the caller | Yes (User) | FR-015 | Same | - |
| POST | `/alerts/<id>/acknowledge/` | Mark one of the caller's alerts as seen | Yes (User, owner) | FR-015 | Added | 11 |
| GET | `/analytics/?from&to` | Category-wise spend breakdown | Yes (User) | FR-016 | Trend moved to its own endpoint | 9 |
| GET | `/analytics/trend/?from&to&granularity` | Daily or weekly spend trend | Yes (User) | FR-017 | Added (split from /analytics) | 9 |
| GET | `/reports/export/?from&to` | Export a CSV of the caller's expenses | Yes (User) | FR-018 | Same | - |
| GET, POST | `/admin/categories/` | List or create master categories | Yes (Admin only) | FR-019, FR-021, SEC-002 | GET added | 10 |
| GET, PUT, PATCH | `/admin/categories/<id>/` | Rename or disable a master category | Yes (Admin only) | FR-019, FR-021, SEC-002 | Update moved here from POST | 10 |
| GET | `/admin/analytics/` | Anonymised system usage totals | Yes (Admin only) | FR-020, FR-021, SEC-002 | Same | - |
| GET | `/health/` | Liveness check for Docker and CI | No | - | Added | - |

Status codes follow SAD 8.1: 200/201 success, 400 validation error, 401 missing or invalid token, 403 wrong role or not the owner, 404 not found, 409 overlapping budget.

## 2. Components (SAD Sections 3.1, 4, 5 and 9), as built

Each SAD component is a Django app or module. The layers of SAD Section 4 map to Django as: views (API/Controller), serializers and `services.py` (Business Logic), Django ORM models (Data Access), and the database (Data).

| SAD component | Where it is in the code | Change from SAD | DEVIATIONS # |
|---|---|---|---|
| Web UI / Dashboard | `templates/`, `smartspend/views.py` | Django templates instead of a separate browser front end | 4 |
| Auth API + Auth Service | `accounts/` (`views.py`, `services.py`, `tokens.py`, `authentication.py`) | Token is a Django signed token, not a JWT | 8 |
| Expense API + Expense Service | `expenses/` (`views.py`, `serializers.py`, `services.py`, `validators.py`) | Input sanitiser `validators.py` added for SEC-003 | 16 |
| Budget API + Budget Service | `budgets/` (`views.py`, `serializers.py`, `services.py`) | Budgets also return computed `spent`, `remaining`, `end_date` | - |
| Alert Engine | `budgets/alerts.py`, triggered by `budgets/signals.py` | Runs from a post_save signal on Expense, inside budgets/ | 14 |
| Report Service + Analytics/Admin API | `reports/` (`services.py`, `views.py`, `serializers.py`) | Admin category management lives here with the other admin endpoints | 10 |
| Repository / ORM Layer | Django ORM models in each app's `models.py` | Django ORM used directly as the repository layer | - |
| Logging / Monitoring | `smartspend/security_log.py`, written to `logs/security.log` | Same | - |
| RBAC (SAD 5) | `smartspend/permissions.py` `IsAdminRole` | Same | - |
| Error handling (SAD 9) | DRF ValidationError (400), `budgets/views.py` `BudgetConflict` (409) | Fewer typed exceptions than listed in SAD 9 | 15 |

Security additions made during Sprint 2:

- SEC-003: free text is trimmed and rejected (400) if it contains control characters or `<` `>` (`expenses/validators.py`).
- SEC-006: users are always returned through an allow-list serializer of `id`, `email`, `role` (`accounts/serializers.py`).
- FR-018: CSV cells that start with `=`, `+`, `-` or `@` get a `'` in front, so a spreadsheet never runs them as formulas (`reports/views.py` `safe_cell`).

## 3. Data design (SAD Section 10, SRS Appendix B), as built

All primary keys are UUIDs. Amounts are `Decimal(10,2)`, never floating point (SAD 8.1).

| Entity | Fields in the code | Change from documents | DEVIATIONS # |
|---|---|---|---|
| User | id, email (unique), username, password (salted hash), role (USER or ADMIN), is_active | `username` added; password hash is in Django's `password` field | 5 |
| Category | id, name (max 50), is_active, owner (empty for master categories) | Same | - |
| Expense | id, user, category, amount (> 0), expense_date, note (max 255), created_at | `created_at` added to order expenses saved on the same day | - |
| Budget | id, user, category, limit_amount (> 0), period (WEEKLY or MONTHLY), start_date | End date is computed (weekly: start + 6 days; monthly: last day of month), not stored | - |
| Alert | id, user, budget, threshold_type ("80" or "100"), created_at, acknowledged | Same | - |

Computed, not stored: a budget's `spent`, `remaining` and `end_date` are worked out on every request from the expenses (FR-011), so a new expense shows up at once (TC-NFR-01).

## 4. Requirement status at v1.0 (SRS)

Every requirement in the SRS is implemented. Test results for the Test Plan cases are in [TEST_RESULTS.md](TEST_RESULTS.md); RTM code references are in [RTM.md](RTM.md).

| Requirement | Status | Main code | Tests |
|---|---|---|---|
| FR-001 Register | Implemented | `accounts/views.py` RegisterView | `tests/test_register.py` |
| FR-002 Reject duplicate email | Implemented | `accounts/services.py` register_user | `tests/test_register.py`, `tests/test_auth_units.py` |
| FR-003 Log in | Implemented | `accounts/views.py` LoginView | `tests/test_login.py` |
| FR-004 Token valid at most 24 h | Implemented | `accounts/tokens.py` | `tests/test_login.py`, `tests/test_token_units.py` |
| FR-005 Add expense | Implemented | `expenses/views.py` ExpenseListCreateView | `tests/test_expenses.py` |
| FR-006 Edit or delete own expense | Implemented | `expenses/views.py` ExpenseDetailView | `tests/test_expense_edit.py` |
| FR-007 Custom categories | Implemented | `expenses/views.py` CategoryListCreateView | `tests/test_categories.py` |
| FR-008 Reject amount of 0 or less | Implemented | `expenses/models.py`, `expenses/serializers.py` | `tests/test_expenses.py`, `tests/test_expense_api_rules.py` |
| FR-009 Create budget | Implemented | `budgets/views.py` BudgetListCreateView | `tests/test_budgets.py` |
| FR-010 Edit budget | Implemented | `budgets/views.py` BudgetDetailView | `tests/test_budget_edit.py` |
| FR-011 Live spent and remaining | Implemented | `budgets/services.py` spent_for | `tests/test_budget_spend.py`, `tests/test_threshold_timing.py` |
| FR-012 No overlapping budgets | Implemented | `budgets/services.py` overlaps_existing | `tests/test_budgets.py` |
| FR-013 Alert at 80% | Implemented | `budgets/alerts.py` | `tests/test_alert_rules.py`, `tests/test_alert_trigger.py` |
| FR-014 Alert when exceeded | Implemented | `budgets/alerts.py` | `tests/test_alert_rules.py` |
| FR-015 List and acknowledge alerts | Implemented | `budgets/views.py` AlertListView, AlertAcknowledgeView | `tests/test_alert_list.py`, `tests/test_alert_acknowledge.py` |
| FR-016 Spend by category | Implemented | `reports/services.py` category_breakdown | `tests/test_analytics.py` |
| FR-017 Daily or weekly trend | Implemented | `reports/services.py` spend_trend | `tests/test_trend.py` |
| FR-018 CSV export | Implemented | `reports/views.py` ExportCsvView | `tests/test_export.py` |
| FR-019 Admin manages master categories | Implemented | `reports/views.py` AdminCategory views | `tests/test_admin_categories.py` |
| FR-020 Anonymised usage totals | Implemented | `reports/services.py` admin_usage_stats | `tests/test_admin_analytics.py` |
| FR-021 Admin-only access | Implemented | `smartspend/permissions.py` IsAdminRole | `tests/test_admin_categories.py`, `tests/test_admin_analytics.py` |
| NFR-001 95% under 2 s at 50 users | Implemented | `reports/views.py` CategoryBreakdownView | `scripts/load_test.py`, `docs/perf/nfr001_results.txt` |
| NFR-002 Recalculation under 1 s | Implemented | `budgets/services.py`, `budgets/signals.py` | `tests/test_threshold_timing.py` |
| SEC-001 Password hashing | Implemented | `accounts/services.py` | `tests/test_register.py` |
| SEC-002 RBAC | Implemented | `smartspend/permissions.py` | `tests/test_security.py` |
| SEC-003 Input validation | Implemented | `expenses/validators.py` | `tests/test_input_validation.py`, `tests/test_expense_units.py` |
| SEC-004 Invalid token gives 401 | Implemented | `accounts/authentication.py` | `tests/test_tokens.py` |
| SEC-005 Security logging | Implemented | `smartspend/security_log.py` | `tests/test_security.py`, `tests/test_login.py` |
| SEC-006 No sensitive fields | Implemented | `accounts/serializers.py` UserSerializer | `tests/test_no_sensitive_fields.py`, `tests/test_me.py` |
