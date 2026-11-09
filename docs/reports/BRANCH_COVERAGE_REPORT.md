# Branch Coverage Report

SmartSpend (Team H5), v1.0. Course Part-3, item 2b-iv.

**Branch coverage** checks that every decision in the code (each `if`, `for` and `while`) went both ways during the tests: the condition was true at least once and false at least once. Line coverage alone can miss this: an `if` whose condition is always true has every line run but its "false" path never tested.

Measured with coverage.py in branch mode (`--cov-branch` in `pytest.ini`) while running the full test suite. Raw output: [coverage_full.txt](coverage_full.txt) (columns `Branch` and `BrPart`) and [coverage.json](coverage.json).

## Summary by module

| Module | Owner | Branches | Branches covered | Decisions with a path not taken | Branch coverage |
|---|---|---|---|---|---|
| `accounts` (Auth) | Member 1 | 10 | 10 | 0 | 100.0% |
| `expenses` (Expenses and categories) | Member 2 | 12 | 11 | 1 | 91.7% |
| `budgets` (Budgets and alerts) | Member 3 | 38 | 36 | 2 | 94.7% |
| `reports` (Reports and admin) | Member 4 | 20 | 19 | 1 | 95.0% |
| `smartspend` (Project settings and shared code) | Shared | 4 | 3 | 1 | 75.0% |
| **Whole project** | | **84** | **79** | **5** | **94.0%** |

"Branches" counts each possible path out of a decision (an `if` has two). "Decisions with a path not taken" counts the `if` and `for` statements where at least one of their paths never ran in the tests.

## Per file (files with decisions)

| File | Branches | Covered | Branch coverage |
|---|---|---|---|
| `accounts/authentication.py` | 4 | 4 | 100% |
| `accounts/services.py` | 4 | 4 | 100% |
| `accounts/views.py` | 2 | 2 | 100% |
| `budgets/alerts.py` | 14 | 12 | 86% |
| `budgets/serializers.py` | 6 | 6 | 100% |
| `budgets/services.py` | 12 | 12 | 100% |
| `budgets/views.py` | 6 | 6 | 100% |
| `expenses/serializers.py` | 4 | 3 | 75% |
| `expenses/services.py` | 4 | 4 | 100% |
| `expenses/validators.py` | 4 | 4 | 100% |
| `reports/serializers.py` | 4 | 3 | 75% |
| `reports/services.py` | 2 | 2 | 100% |
| `reports/views.py` | 14 | 14 | 100% |
| `smartspend/permissions.py` | 2 | 2 | 100% |
| `smartspend/settings.py` | 2 | 1 | 50% |

## Branches not taken, and why

| File | Decision (line) | Path never taken | Why |
|---|---|---|---|
| `budgets/alerts.py` | 18: `if limit <= Decimal("0")` | true | A limit of 0 or less is refused by the model and serializer, so this guard cannot be reached. |
| `budgets/alerts.py` | 57: `if expense.expense_date <= budget_end` (inside the loop) | false | The query already keeps only budgets that start on or before the expense date; no test adds an expense after a budget's end while that budget is still selected. |
| `expenses/serializers.py` | 41: `if not value` | true | A blank category name is refused by the field before this check. |
| `reports/serializers.py` | 16: `if not value` | true | Same as above, for master categories. |
| `smartspend/settings.py` | 55: `if os.environ.get("POSTGRES_DB")` | true | PostgreSQL is used only under Docker Compose; tests run on SQLite. |

## Conclusion

79 of 84 branches are covered (94.0%). All five branches not taken are defensive guards or the deployment-only database setting; none is part of a user-facing rule that is left untested.
