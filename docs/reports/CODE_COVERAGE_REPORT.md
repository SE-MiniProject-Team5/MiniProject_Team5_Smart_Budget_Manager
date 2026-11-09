# Code Coverage Report (line coverage)

SmartSpend (Team H5), v1.0. Course Part-3, item 2b-iii. Test Plan Section 5: each Service-layer module needs at least **70% line coverage**.

Measured with coverage.py through pytest-cov while running the full test suite (`pytest`, settings in `pytest.ini`). Migrations and empty `__init__.py` files are left out of the per-file table but are counted in the raw report. Raw output: [coverage_full.txt](coverage_full.txt) and [coverage.json](coverage.json).

## Summary by module

| Module | Owner | Statements | Covered | Missed | Line coverage | Target 70% |
|---|---|---|---|---|---|---|
| `accounts` (Auth) | Member 1 | 122 | 122 | 0 | 100.0% | Met |
| `expenses` (Expenses and categories) | Member 2 | 106 | 105 | 1 | 99.1% | Met |
| `budgets` (Budgets and alerts) | Member 3 | 199 | 198 | 1 | 99.5% | Met |
| `reports` (Reports and admin) | Member 4 | 121 | 120 | 1 | 99.2% | Met |
| `smartspend` (Project settings and shared code) | Shared | 59 | 50 | 9 | 84.7% | Met |
| **Whole project** (including migrations) | | **636** | **624** | **12** | **98.1%** | **Met** |

## Per file

| File | Statements | Missed | Line coverage | Missed lines |
|---|---|---|---|---|
| `accounts/admin.py` | 1 | 0 | 100% | - |
| `accounts/apps.py` | 4 | 0 | 100% | - |
| `accounts/authentication.py` | 25 | 0 | 100% | - |
| `accounts/models.py` | 14 | 0 | 100% | - |
| `accounts/serializers.py` | 17 | 0 | 100% | - |
| `accounts/services.py` | 15 | 0 | 100% | - |
| `accounts/tokens.py` | 8 | 0 | 100% | - |
| `accounts/urls.py` | 3 | 0 | 100% | - |
| `accounts/views.py` | 35 | 0 | 100% | - |
| `budgets/admin.py` | 1 | 0 | 100% | - |
| `budgets/alerts.py` | 27 | 1 | 96% | 19 |
| `budgets/apps.py` | 6 | 0 | 100% | - |
| `budgets/models.py` | 27 | 0 | 100% | - |
| `budgets/permissions.py` | 5 | 0 | 100% | - |
| `budgets/serializers.py` | 38 | 0 | 100% | - |
| `budgets/services.py` | 30 | 0 | 100% | - |
| `budgets/signals.py` | 12 | 0 | 100% | - |
| `budgets/urls.py` | 3 | 0 | 100% | - |
| `budgets/views.py` | 50 | 0 | 100% | - |
| `expenses/admin.py` | 1 | 0 | 100% | - |
| `expenses/apps.py` | 4 | 0 | 100% | - |
| `expenses/models.py` | 24 | 0 | 100% | - |
| `expenses/permissions.py` | 5 | 0 | 100% | - |
| `expenses/serializers.py` | 29 | 1 | 97% | 42 |
| `expenses/services.py` | 6 | 0 | 100% | - |
| `expenses/urls.py` | 3 | 0 | 100% | - |
| `expenses/validators.py` | 9 | 0 | 100% | - |
| `expenses/views.py` | 25 | 0 | 100% | - |
| `reports/admin.py` | 1 | 0 | 100% | - |
| `reports/apps.py` | 4 | 0 | 100% | - |
| `reports/models.py` | 1 | 0 | 100% | - |
| `reports/serializers.py` | 17 | 1 | 94% | 17 |
| `reports/services.py` | 24 | 0 | 100% | - |
| `reports/urls.py` | 3 | 0 | 100% | - |
| `reports/views.py` | 71 | 0 | 100% | - |
| `smartspend/asgi.py` | 4 | 4 | 0% | 10, 12, 14, 16 |
| `smartspend/permissions.py` | 12 | 0 | 100% | - |
| `smartspend/security_log.py` | 4 | 0 | 100% | - |
| `smartspend/settings.py` | 25 | 1 | 96% | 56 |
| `smartspend/urls.py` | 4 | 0 | 100% | - |
| `smartspend/views.py` | 6 | 0 | 100% | - |
| `smartspend/wsgi.py` | 4 | 4 | 0% | 10, 12, 14, 16 |

## Lines not covered, and why

- `budgets/alerts.py:19`: `return []` when a budget limit is 0 or less. A defensive guard: the model and serializer already refuse such a limit, so no test can create one.
- `expenses/serializers.py:42`: "Category name cannot be blank." Django REST Framework's CharField already refuses a blank or all-space name before this check runs, so it is a defensive second check.
- `reports/serializers.py:17`: Same defensive blank-name check for master categories, also caught earlier by the field itself.
- `smartspend/settings.py:56`: The PostgreSQL settings, used only when `POSTGRES_DB` is set (Docker Compose). Tests run on SQLite.
- `smartspend/asgi.py`: Server entry point for deployment; not imported by tests.
- `smartspend/wsgi.py`: Server entry point for deployment; not imported by tests.

## Conclusion

Every module is well above the 70% line coverage target, and the whole project is at 98.1%. The few missed lines are defensive checks that earlier validation already enforces, and deployment-only settings and entry points.
