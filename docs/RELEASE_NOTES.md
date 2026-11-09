# SmartSpend v1.0 Release Notes

v1.0 is the end of Sprint 2. Development is frozen at this version (course Part-2 brief, Sprint 2 item d).
The release is the git tag `v1.0` on `main`.

## Sprint 1

- Accounts: register, log in with a 24-hour Bearer token, duplicate email rejected (FR-001 to FR-004).
- Expenses: add, edit, delete and list own expenses; custom categories; amount must be above 0 (FR-005 to FR-008).
- Budgets: weekly or monthly budgets per category, overlapping budgets rejected, live spent and remaining (FR-009 to FR-012).
- Analytics: spend by category for a date range (FR-016).
- Security: password hashing, admin-only endpoints, invalid token gives 401, security event log (SEC-001, SEC-002, SEC-004, SEC-005).
- CI with GitHub Actions on every pull request; Sprint 1 demo video.

## Sprint 2

- Alerts: an alert at 80% of a budget and a second one when it is exceeded, created as soon as an expense is saved; list and acknowledge alerts (FR-013 to FR-015).
- Reports: daily or weekly spend trend (FR-017) and CSV export with spreadsheet formula protection (FR-018).
- Admin: manage master categories (add, rename, disable) and anonymised usage totals, admins only (FR-019 to FR-021).
- Security: server-side input sanitisation (SEC-003); no password, hash or secret in any response, plus GET /api/v1/auth/me/ (SEC-006).
- Performance: load test with 50 concurrent users (NFR-001) and a 1-second recalculation test (NFR-002).
- Unit tests and coverage reports for every module; Test Plan results; RTM code references; design updates; Sprint 2 demo video.

## Evidence

| What | Where |
|---|---|
| Test Plan results (13 test cases) | `docs/TEST_RESULTS.md` |
| RTM code references | `docs/RTM.md` |
| Coverage per module | `docs/coverage/` |
| Load test result | `docs/perf/nfr001_results.txt` |
| Changes from the SAD and SRS | `docs/DESIGN_UPDATES.md`, `DEVIATIONS.md` |
| Demo scripts and videos | `docs/demo/` |

## Known limitations

- The UI is a set of Django templates; most features are used through the REST API (DEVIATIONS #4).
- Local runs and CI use SQLite; PostgreSQL is used only through Docker Compose (DEVIATIONS #6).
- Administrators are created by changing a registered user's role with `python manage.py shell` (see README).
