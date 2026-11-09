# Unit Test Report

SmartSpend (Team H5), v1.0. Course Part-3, item 2b-i. Test Plan Sections 4 and 7 ("Automated unit test reports").

## Summary

| Item | Value |
|---|---|
| Test files | 33 |
| Test cases run | 207 |
| Passed | 207 |
| Failed | 0 |
| Skipped | 0 |
| Tool | pytest with pytest-django and pytest-cov (versions in `requirements.txt`) |
| Database | A fresh SQLite test database, created and destroyed by pytest-django for every run |
| Where it runs | Locally with `pytest`, and in GitHub Actions on every pull request and every push to `main` |
| Full run log | [unit_test_run.txt](unit_test_run.txt) (output of `pytest -v`) |
| Machine-readable results | [unit_tests.xml](unit_tests.xml) (JUnit XML) |

A test case is one test function, or one set of inputs of a parametrised test (`@pytest.mark.parametrize`), so the count is higher than the number of `def test_` functions.

**Test levels** (Test Plan Section 4):

- **Unit:** calls one function, class or serializer directly (for example `register_user`, `evaluate_budget`, `spend_trend`, `clean_text`), so a failure points at exactly one rule.
- **API:** sends a request through Django REST Framework's test client to an endpoint and checks the status code and response, with a real test database behind it (Test Plan level 2, integration).

## Results by module

| Module | Unit test cases | API test cases | Total | Passed | Failed |
|---|---|---|---|---|---|
| Auth (accounts, Member 1) | 14 | 22 | 36 | 36 | 0 |
| Expenses and categories (expenses, Member 2) | 15 | 47 | 62 | 62 | 0 |
| Budgets and alerts (budgets, Member 3) | 29 | 25 | 54 | 54 | 0 |
| Reports and admin (reports, Member 4) | 14 | 30 | 44 | 44 | 0 |
| Shared (smartspend) | 4 | 7 | 11 | 11 | 0 |
| **All** | | | **207** | **207** | **0** |

## Auth (accounts, Member 1)

| Test file | Level | Requirements | Test cases | Result |
|---|---|---|---|---|
| `tests/test_auth_units.py` | Unit | FR-001, FR-002, FR-003, SEC-001 | 7 | Pass |
| `tests/test_token_units.py` | Unit | FR-004, SEC-004 | 7 | Pass |
| `tests/test_register.py` | API | FR-001, FR-002, SEC-001, SEC-006 | 6 | Pass |
| `tests/test_login.py` | API | FR-003, FR-004, SEC-005 | 6 | Pass |
| `tests/test_tokens.py` | API | SEC-004, SEC-005 | 5 | Pass |
| `tests/test_me.py` | API | SEC-006 | 3 | Pass |
| `tests/test_no_sensitive_fields.py` | API | SEC-006 | 2 | Pass |

**`tests/test_auth_units.py`**

- `test_register_stores_a_hash_not_the_password`: Pass
- `test_register_rejects_same_email_in_other_case`: Pass
- `test_register_race_on_same_email_is_still_a_duplicate`: Pass
- `test_login_check_accepts_right_password_any_email_case`: Pass
- `test_login_check_rejects_wrong_password`: Pass
- `test_login_check_rejects_unknown_email`: Pass
- `test_login_check_rejects_disabled_account`: Pass

**`tests/test_token_units.py`**

- `test_token_round_trip_gives_back_the_user_id`: Pass
- `test_tampered_token_is_refused`: Pass
- `test_token_older_than_the_limit_is_refused`: Pass
- `test_user_is_shown_by_email`: Pass
- `test_bearer_header_with_extra_parts_gives_401`: Pass
- `test_other_auth_schemes_are_ignored_and_give_401`: Pass
- `test_token_lifetime_is_24_hours`: Pass

**`tests/test_register.py`**

- `test_register_success_returns_201_and_creates_user`: Pass
- `test_password_is_stored_hashed`: Pass
- `test_short_password_rejected_with_400`: Pass
- `test_invalid_email_rejected_with_400`: Pass
- `test_duplicate_email_rejected_with_409_ignoring_case`: Pass
- `test_response_never_contains_password`: Pass

**`tests/test_login.py`**

- `test_login_with_valid_credentials_returns_token`: Pass
- `test_token_lifetime_is_at_most_24_hours`: Pass
- `test_login_email_ignores_capital_letters`: Pass
- `test_wrong_password_gives_401_and_is_logged`: Pass
- `test_unknown_email_gives_401`: Pass
- `test_missing_password_gives_400`: Pass

**`tests/test_tokens.py`**

- `test_valid_token_is_accepted`: Pass
- `test_no_token_gives_401`: Pass
- `test_malformed_token_gives_401_and_is_logged`: Pass
- `test_expired_token_gives_401`: Pass
- `test_token_of_deleted_user_gives_401`: Pass

**`tests/test_me.py`**

- `test_me_returns_only_safe_fields`: Pass
- `test_me_needs_login`: Pass
- `test_register_response_has_only_safe_fields`: Pass

**`tests/test_no_sensitive_fields.py`**

- `test_no_endpoint_leaks_secrets`: Pass
- `test_error_responses_do_not_leak`: Pass

## Expenses and categories (expenses, Member 2)

| Test file | Level | Requirements | Test cases | Result |
|---|---|---|---|---|
| `tests/test_expense_units.py` | Unit | FR-007, FR-008, SEC-003 | 15 | Pass |
| `tests/test_expense_api_rules.py` | API | FR-005, FR-007, FR-008, SEC-003 | 6 | Pass |
| `tests/test_expenses.py` | API | FR-005, FR-008 | 10 | Pass |
| `tests/test_expense_edit.py` | API | FR-006 | 6 | Pass |
| `tests/test_categories.py` | API | FR-007 | 5 | Pass |
| `tests/test_input_validation.py` | API | SEC-003 | 20 | Pass |

**`tests/test_expense_units.py`**

- `test_active_predefined_category_is_allowed`: Pass
- `test_inactive_category_is_refused`: Pass
- `test_own_custom_category_is_allowed`: Pass
- `test_someone_elses_category_is_refused`: Pass
- `test_category_is_shown_by_name`: Pass
- `test_expense_is_shown_by_date_and_amount`: Pass
- `test_clean_text_trims_spaces`: Pass
- `test_clean_text_keeps_normal_punctuation`: Pass
- `test_clean_text_rejects_control_characters[a\tb]`: Pass
- `test_clean_text_rejects_control_characters[a\nb]`: Pass
- `test_clean_text_rejects_control_characters[a\x00b]`: Pass
- `test_clean_text_rejects_control_characters[a\x7fb]`: Pass
- `test_clean_text_rejects_angle_brackets[<b>]`: Pass
- `test_clean_text_rejects_angle_brackets[a < b]`: Pass
- `test_clean_text_rejects_angle_brackets[x>y]`: Pass

**`tests/test_expense_api_rules.py`**

- `test_category_name_of_only_spaces_is_refused`: Pass
- `test_category_name_over_50_characters_is_refused`: Pass
- `test_zero_amount_is_refused`: Pass
- `test_negative_amount_is_refused`: Pass
- `test_note_is_saved_trimmed`: Pass
- `test_a_user_sees_only_their_own_expenses`: Pass

**`tests/test_expenses.py`**

- `test_add_valid_expense_returns_201`: Pass
- `test_zero_or_negative_amount_rejected[0]`: Pass
- `test_zero_or_negative_amount_rejected[-5]`: Pass
- `test_note_longer_than_255_rejected`: Pass
- `test_inactive_category_rejected`: Pass
- `test_other_users_custom_category_rejected`: Pass
- `test_own_custom_category_allowed`: Pass
- `test_owner_in_json_is_ignored`: Pass
- `test_list_shows_only_own_expenses`: Pass
- `test_anonymous_caller_refused`: Pass

**`tests/test_expense_edit.py`**

- `test_owner_can_edit_expense`: Pass
- `test_owner_can_change_one_field`: Pass
- `test_edit_still_rejects_zero_amount`: Pass
- `test_owner_can_delete_expense`: Pass
- `test_other_user_cannot_edit_or_delete`: Pass
- `test_unknown_id_gives_404`: Pass

**`tests/test_categories.py`**

- `test_list_shows_predefined_and_own_active_categories`: Pass
- `test_create_custom_category`: Pass
- `test_name_longer_than_50_rejected`: Pass
- `test_blank_name_rejected`: Pass
- `test_anonymous_caller_refused`: Pass

**`tests/test_input_validation.py`**

- `test_html_in_note_rejected[<script>alert(1)</script>]`: Pass
- `test_html_in_note_rejected[<b>bold</b>]`: Pass
- `test_html_in_note_rejected[a > b]`: Pass
- `test_control_characters_in_note_rejected[line1\nline2]`: Pass
- `test_control_characters_in_note_rejected[tab\there]`: Pass
- `test_control_characters_in_note_rejected[null\x00byte]`: Pass
- `test_note_is_trimmed`: Pass
- `test_html_in_category_name_rejected`: Pass
- `test_html_rejected_on_edit_too`: Pass
- `test_malformed_values_rejected[overrides0]`: Pass
- `test_malformed_values_rejected[overrides1]`: Pass
- `test_malformed_values_rejected[overrides2]`: Pass
- `test_malformed_values_rejected[overrides3]`: Pass
- `test_malformed_values_rejected[overrides4]`: Pass
- `test_malformed_values_rejected[overrides5]`: Pass
- `test_malformed_values_rejected[overrides6]`: Pass
- `test_missing_required_field_rejected[category]`: Pass
- `test_missing_required_field_rejected[amount]`: Pass
- `test_missing_required_field_rejected[expense_date]`: Pass
- `test_body_that_is_not_json_object_rejected`: Pass

## Budgets and alerts (budgets, Member 3)

| Test file | Level | Requirements | Test cases | Result |
|---|---|---|---|---|
| `tests/test_budget_units.py` | Unit | FR-009 to FR-014 | 18 | Pass |
| `tests/test_budget_spend.py` | Unit | FR-011 | 2 | Pass |
| `tests/test_alert_rules.py` | Unit | FR-013, FR-014 | 6 | Pass |
| `tests/test_alerts.py` | Unit | FR-013, FR-014, FR-015 | 3 | Pass |
| `tests/test_budgets.py` | API | FR-009, FR-012 | 6 | Pass |
| `tests/test_budget_edit.py` | API | FR-010 | 7 | Pass |
| `tests/test_budget_spent_fields.py` | API | FR-011 | 2 | Pass |
| `tests/test_alert_trigger.py` | API | FR-013, FR-014 | 3 | Pass |
| `tests/test_alert_list.py` | API | FR-015 | 3 | Pass |
| `tests/test_alert_acknowledge.py` | API | FR-015 | 3 | Pass |
| `tests/test_threshold_timing.py` | API | FR-011, NFR-002 | 1 | Pass |

**`tests/test_budget_units.py`**

- `test_overlapping_budget_is_detected`: Pass
- `test_next_month_does_not_overlap`: Pass
- `test_budget_being_edited_does_not_clash_with_itself`: Pass
- `test_spent_counts_only_this_budgets_period_category_and_user`: Pass
- `test_spent_is_zero_with_no_expenses`: Pass
- `test_serializer_refuses_inactive_category`: Pass
- `test_just_under_80_percent_gives_no_alert`: Pass
- `test_exactly_100_percent_gives_only_the_warning`: Pass
- `test_jumping_past_100_percent_gives_both_alerts_once`: Pass
- `test_budget_is_shown_by_category_period_and_limit`: Pass
- `test_weekly_budget_ends_six_days_later`: Pass
- `test_monthly_budget_ends_on_last_day_of_month`: Pass
- `test_monthly_budget_in_leap_year_february`: Pass
- `test_category_rule_allows_active_predefined`: Pass
- `test_category_rule_refuses_inactive`: Pass
- `test_category_rule_refuses_someone_elses`: Pass
- `test_serializer_refuses_zero_limit`: Pass
- `test_serializer_refuses_unknown_period`: Pass

**`tests/test_budget_spend.py`**

- `test_spent_and_remaining_are_returned`: Pass
- `test_new_expense_is_reflected_on_next_request`: Pass

**`tests/test_alert_rules.py`**

- `test_warning_created_at_80_percent`: Pass
- `test_no_alert_below_80_percent`: Pass
- `test_exceeded_alert_above_100_percent`: Pass
- `test_exactly_100_percent_does_not_create_exceeded_alert`: Pass
- `test_alerts_are_not_duplicated`: Pass
- `test_evaluate_for_expense_checks_matching_budget`: Pass

**`tests/test_alerts.py`**

- `test_warning_alert_creation`: Pass
- `test_exceeded_budget_alert_creation`: Pass
- `test_alert_can_be_acknowledged`: Pass

**`tests/test_budgets.py`**

- `test_create_monthly_budget`: Pass
- `test_zero_budget_limit_rejected`: Pass
- `test_negative_budget_limit_rejected`: Pass
- `test_second_budget_same_month_rejected`: Pass
- `test_weekly_inside_monthly_rejected`: Pass
- `test_next_month_is_allowed`: Pass

**`tests/test_budget_edit.py`**

- `test_owner_can_change_limit`: Pass
- `test_editing_does_not_clash_with_itself`: Pass
- `test_edit_into_another_budgets_period_gives_409`: Pass
- `test_edit_rejects_zero_limit`: Pass
- `test_owner_can_delete_budget`: Pass
- `test_other_user_cannot_edit_or_delete`: Pass
- `test_list_shows_only_own_budgets`: Pass

**`tests/test_budget_spent_fields.py`**

- `test_budget_detail_shows_spent_and_remaining`: Pass
- `test_new_budget_starts_with_nothing_spent`: Pass

**`tests/test_alert_trigger.py`**

- `test_expense_save_triggers_warning_alert`: Pass
- `test_expense_save_triggers_exceeded_alert`: Pass
- `test_expense_save_succeeds_if_alert_evaluation_fails`: Pass

**`tests/test_alert_list.py`**

- `test_lists_only_own_unacknowledged_alerts`: Pass
- `test_alert_shows_up_after_spending_through_the_api`: Pass
- `test_alerts_need_login`: Pass

**`tests/test_alert_acknowledge.py`**

- `test_acknowledge_hides_alert`: Pass
- `test_cannot_acknowledge_someone_elses_alert`: Pass
- `test_acknowledging_does_not_recreate_the_alert`: Pass

**`tests/test_threshold_timing.py`**

- `test_spend_and_alert_update_within_one_second`: Pass

## Reports and admin (reports, Member 4)

| Test file | Level | Requirements | Test cases | Result |
|---|---|---|---|---|
| `tests/test_report_units.py` | Unit | FR-016 to FR-020 | 14 | Pass |
| `tests/test_analytics.py` | API | FR-016 | 8 | Pass |
| `tests/test_trend.py` | API | FR-017 | 7 | Pass |
| `tests/test_export.py` | API | FR-018 | 4 | Pass |
| `tests/test_admin_categories.py` | API | FR-019, FR-021 | 8 | Pass |
| `tests/test_admin_analytics.py` | API | FR-020, FR-021 | 3 | Pass |

**`tests/test_report_units.py`**

- `test_breakdown_is_largest_first_with_grand_total`: Pass
- `test_breakdown_of_empty_range_is_zero`: Pass
- `test_daily_trend_lists_every_day_with_zeros`: Pass
- `test_weekly_trend_groups_from_monday`: Pass
- `test_export_rows_are_oldest_first_and_inside_range`: Pass
- `test_usage_stats_are_counts_only`: Pass
- `test_safe_cell_disarms_formulas[=SUM(A1)]`: Pass
- `test_safe_cell_disarms_formulas[+1]`: Pass
- `test_safe_cell_disarms_formulas[-1]`: Pass
- `test_safe_cell_disarms_formulas[@cmd]`: Pass
- `test_safe_cell_leaves_normal_text_alone`: Pass
- `test_admin_category_name_is_trimmed`: Pass
- `test_admin_category_bad_names_are_refused[   ]`: Pass
- `test_admin_category_bad_names_are_refused[<b>Rent</b>]`: Pass

**`tests/test_analytics.py`**

- `test_breakdown_groups_totals_by_category`: Pass
- `test_dates_outside_range_are_ignored`: Pass
- `test_other_users_expenses_are_not_counted`: Pass
- `test_bad_dates_give_400[params0]`: Pass
- `test_bad_dates_give_400[params1]`: Pass
- `test_bad_dates_give_400[params2]`: Pass
- `test_bad_dates_give_400[params3]`: Pass
- `test_anonymous_caller_refused`: Pass

**`tests/test_trend.py`**

- `test_daily_trend_lists_every_day_with_zeros`: Pass
- `test_weekly_trend_groups_by_monday`: Pass
- `test_bad_parameters_give_400[params0]`: Pass
- `test_bad_parameters_give_400[params1]`: Pass
- `test_bad_parameters_give_400[params2]`: Pass
- `test_bad_parameters_give_400[params3]`: Pass
- `test_trend_needs_login`: Pass

**`tests/test_export.py`**

- `test_export_returns_csv_of_own_expenses_in_range`: Pass
- `test_formula_like_text_is_neutralised`: Pass
- `test_export_bad_dates_give_400`: Pass
- `test_export_needs_login`: Pass

**`tests/test_admin_categories.py`**

- `test_admin_lists_all_master_categories`: Pass
- `test_admin_adds_master_category`: Pass
- `test_admin_renames_category`: Pass
- `test_disabling_keeps_existing_expenses`: Pass
- `test_admin_cannot_delete_category`: Pass
- `test_users_own_category_is_not_managed_here`: Pass
- `test_blank_or_html_name_rejected`: Pass
- `test_regular_user_gets_403`: Pass

**`tests/test_admin_analytics.py`**

- `test_admin_sees_totals_only`: Pass
- `test_regular_user_gets_403`: Pass
- `test_anonymous_gets_401`: Pass

## Shared (smartspend)

| Test file | Level | Requirements | Test cases | Result |
|---|---|---|---|---|
| `tests/test_security.py` | Unit | SEC-002, SEC-005 | 4 | Pass |
| `tests/test_smoke.py` | API | Health check, FR-002, FR-008 | 4 | Pass |
| `tests/test_layout.py` | API | TECH-03 (UI layout) | 3 | Pass |

**`tests/test_security.py`**

- `test_regular_user_gets_403_and_is_logged`: Pass
- `test_admin_user_is_allowed`: Pass
- `test_anonymous_is_refused_and_logged`: Pass
- `test_log_entry_has_timestamp_account_and_endpoint`: Pass

**`tests/test_smoke.py`**

- `test_duplicate_email_rejected`: Pass
- `test_expense_amount_must_be_positive`: Pass
- `test_health_endpoint`: Pass
- `test_home_page_renders`: Pass

**`tests/test_layout.py`**

- `test_home_page_has_nav`: Pass
- `test_form_errors_partial_shows_field_error`: Pass
- `test_form_errors_partial_empty_for_valid_form`: Pass

## Conclusion

All 207 test cases pass. Every functional requirement FR-001 to FR-021, both non-functional requirements and all six security requirements have at least one automated test. Coverage per module is in [CODE_COVERAGE_REPORT.md](CODE_COVERAGE_REPORT.md) and [BRANCH_COVERAGE_REPORT.md](BRANCH_COVERAGE_REPORT.md).
