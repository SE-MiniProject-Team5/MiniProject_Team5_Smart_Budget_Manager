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

## Maintenance

Add a new row whenever code differs from the submitted documents. Keep the same five columns, and leave no blank line between rows.