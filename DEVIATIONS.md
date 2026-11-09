# Deviation Log

This document records every place where the code differs from the documents we submitted (SRS, SAD, Test Plan). Each deviation is explained at the final demo.

| # | Document & section | What the document says | What we actually did | Why |
|---|---|---|---|---|
| 1 | Test Plan s6 (Test Environment) | CI via Jenkins or an equivalent tool | GitHub Actions | The course Part-2 brief specifies GitHub Actions |
| 2 | Test Plan s10 (Schedule & Responsibilities) | Sprints 1-6 | Two sprints of 5 days each | The course Part-2 brief fixes two sprints |
| 3 | SRS s2.5 (Design and Implementation Constraints) | Python/Django or JavaScript (MERN) | Python, Django and Django REST Framework | Team decision |
| 4 | SAD s8 (API Design) | Browser front end consuming a pure REST JSON API | Django templates for the UI plus a REST API under /api/v1 | Simpler UI for the two-sprint timeline |
| 5 | SAD s10 (Database Design) | User has user_id, email, password_hash, role | The User model also has a username field; login is by email | Django's base user model requires a username field |
| 6 | SRS s2.4 (Operating Environment), Test Plan s6 | PostgreSQL/MySQL; backend and database run in Docker | SQLite for local runs and CI; PostgreSQL only through docker-compose | Tests and CI run with no database setup |
| 7 | SAD s8 (API Design) | Paths written without a trailing slash, e.g. /api/v1/auth/register | Paths end with a slash, e.g. /api/v1/auth/register/ | Django's URL convention (APPEND_SLASH) |
| 8 | SRS Appendix A (Glossary) | Session token is a JWT | Signed, timestamped token from Django's signing module (24-hour expiry), sent as Authorization: Bearer <token> | Same behaviour (signed, expiring, Bearer) without adding a new package |
| 9 | SAD s8 (API Design) | GET /api/v1/analytics returns the category breakdown and the trend data (FR-016, FR-017) | Two endpoints: GET /api/v1/analytics/ for the breakdown and GET /api/v1/analytics/trend/ for the daily or weekly trend | The two answers have different shapes; a separate endpoint keeps each response simple for its chart |
| 10 | SAD s8 (API Design) | POST /api/v1/admin/categories creates or updates a master category | POST /api/v1/admin/categories/ creates; PUT or PATCH /api/v1/admin/categories/<id>/ renames or disables; GET lists them | An update needs the id of the category; this follows the same pattern as the other endpoints |
| 11 | SAD s8 (API Design) | Only GET /api/v1/alerts is listed for alerts | Added POST /api/v1/alerts/<id>/acknowledge/ | FR-015 requires that alerts can be acknowledged, which needs its own endpoint |
| 12 | SAD s8 (API Design) | No profile or category endpoints for users | Added GET /api/v1/auth/me/ (own profile) and GET/POST /api/v1/categories/ (custom categories) | /auth/me/ shows SEC-006 (only id, email, role returned); /categories/ is needed for FR-007 custom categories |
| 13 | SAD s8 (API Design) | PUT for updating expenses and budgets; no DELETE for budgets | PUT and PATCH for expenses and budgets; DELETE for budgets too | Django REST Framework's standard detail views provide these; ownership is still checked on every one |
| 14 | SAD s3.1 and Seq. Diagram 1 | After an expense is saved, the Alert Engine checks the budget thresholds | The check runs from a Django post_save signal on Expense (budgets/signals.py); if it fails, the error is logged and the expense is still saved | Keeps the Expense Service independent of the Budget code, and a failed alert check never loses the user's expense |
| 15 | SAD s9 (Error Handling) | Services raise typed exceptions such as InvalidAmountError and DuplicateBudgetPeriodError | Validation errors are Django REST Framework ValidationErrors (400); an overlapping budget raises BudgetConflict (409) | DRF already maps validation errors to 400 with field messages; only the 409 case needed its own exception |
| 16 | SAD s5 (Security Architecture) | All input validated and sanitized at the Service layer | Free text (notes, category names) is trimmed and rejected with 400 if it contains control characters or < >; it is never silently changed | SEC-003's acceptance criterion is that invalid input returns 400 |
| 17 | Test Plan s10 (Schedule & Responsibilities) | Final test report compiled by Member 4 | Test results and RTM code references completed by Member 3 (DOC-01) | Sprint 2 work was rebalanced so every member had an even workload |

## Maintenance

Add a new row whenever code differs from the submitted documents. Keep the same five columns, and leave no blank line between rows.
