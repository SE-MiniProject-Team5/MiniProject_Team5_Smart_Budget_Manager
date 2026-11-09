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
