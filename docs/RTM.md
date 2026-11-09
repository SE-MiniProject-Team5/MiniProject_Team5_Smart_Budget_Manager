# Requirement Traceability Matrix: Code References (SRS Appendix C)

This file completes the **Code Ref** column of the RTM in SRS Appendix C (SRS_H5.pdf), which was left as TBD until implementation.
Architecture Ref, Design Ref and Test Case ID are copied from the SRS unchanged. Test results are in `docs/TEST_RESULTS.md`.

| Req ID | Brief Description | Architecture Ref | Design Ref | Code Ref | Test Case ID |
|---|---|---|---|---|---|
| FR-001 | User registration | Auth Service (3.1) | Seq. Diagram 2 | `accounts/views.py` RegisterView; `accounts/services.py` register_user | TC-FUN-01 |
| FR-003 | User authentication | Auth Service (3.1) | Seq. Diagram 2 | `accounts/views.py` LoginView; `accounts/services.py` authenticate_user; `accounts/tokens.py` issue_token | TC-FUN-02 |
| FR-005 | Add expense entry | Expense Service (3.1) | Seq. Diagram 1 | `expenses/views.py` ExpenseListCreateView; `expenses/serializers.py` ExpenseSerializer | TC-FUN-03 |
| FR-008 | Reject non-positive amount | Expense Service (3.1) | Seq. Diagram 1 | `expenses/models.py` Expense.amount (MinValueValidator); `expenses/serializers.py` ExpenseSerializer | TC-FUN-04 |
| FR-009 | Create budget | Budget Service (3.1) | Class design (4.1) | `budgets/views.py` BudgetListCreateView; `budgets/serializers.py` BudgetSerializer; `budgets/services.py` overlaps_existing | TC-FUN-05 |
| FR-011 | Real-time threshold recalculation | Alert Engine (3.1) | Seq. Diagram 1 | `budgets/services.py` spent_for; `budgets/signals.py` (runs on every expense save) | TC-NFR-01 |
| FR-013 | Alert at 80% threshold | Alert Engine (3.1) | Seq. Diagram 1 | `budgets/alerts.py` evaluate_budget, evaluate_for_expense; `budgets/views.py` AlertListView | TC-FUN-06 |
| FR-016 | Category-wise spend breakdown | Report Service (3.1) | API Design (4.2) | `reports/services.py` category_breakdown; `reports/views.py` CategoryBreakdownView | TC-FUN-07 |
| FR-019 | Admin manages categories | Admin/API layer (3.1) | API Design (4.2) | `reports/views.py` AdminCategoryListCreateView, AdminCategoryDetailView; `reports/serializers.py` AdminCategorySerializer | TC-FUN-08 |
| SEC-001 | Password hashing | Auth Service (3.1) | Seq. Diagram 2 | `accounts/services.py` register_user (Django create_user, PBKDF2 hash) | TC-SEC-01 |
| SEC-002 | RBAC enforcement | API/Controller layer (3.1) | API Design (4.2) | `smartspend/permissions.py` IsAdminRole; `accounts/models.py` User.role | TC-SEC-02 |
| SEC-004 | Reject invalid session token | API/Controller layer (3.1) | API Design (4.2) | `accounts/authentication.py` BearerTokenAuthentication; `accounts/tokens.py` read_token | TC-SEC-03 |
| NFR-001 | Dashboard response time | Full stack (3.1) | Section 6.4 (perf.) | `reports/views.py` CategoryBreakdownView; `scripts/load_test.py` | TC-NFR-02 |
