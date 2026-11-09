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
