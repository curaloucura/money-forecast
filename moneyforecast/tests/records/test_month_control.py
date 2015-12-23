import pytest


pytest_plugins = ['tests.records.fixtures']


@pytest.mark.django_db
class TestMonthControl:
    def test_is_current(self, month_control):
        assert month_control.is_current()

    def test_get_initial_balance_starts_with_zero(self, month_control):
        assert month_control.get_initial_balance() == 0

    def test_upcoming_records_is_empty(self, month_control):
        assert month_control.get_upcoming_records() == []

    def test_upcoming_records_has_one(self, outcome_future, month_control):
        upcoming_records = month_control.get_upcoming_records()
        assert len(upcoming_records) == 1

    def test_next_month_returns_no_record(
            self, outcome_future, month_control, next_month_future):
        month_control.set_month_and_year(
            next_month_future.month, next_month_future.year)
        upcoming_records = month_control.get_upcoming_records()
        assert len(upcoming_records) == 0

    def test_get_savings_total(self, savings_current, month_control):
        assert month_control.get_savings_totals()['total'] == 1

    def test_get_records_matches_date_of_records(
            self, outcome_future, month_control):
        upcoming_records = month_control.get_upcoming_records()
        assert upcoming_records[0][0] == upcoming_records[0][1].start_date

    def test_record_first_day_with_timezone_is_returned(
            self, outcome_current, month_control, current_date):
        first_day = current_date.replace(day=1)
        outcome_current.start_date = first_day
        outcome_current.save()
        upcoming_records = month_control._get_records_by_type(
            outcome_current.category.type_category, False)
        assert len(upcoming_records)

    def test_remaining_budget(self, budget, month_control):
        assert month_control.budget == 1
        month_control._set_budget_amounts(0)
        assert month_control.remaining_budget == 1
        month_control._set_budget_amounts(1)
        assert month_control.remaining_budget == 0

    def test_outcome_with_budget(self, budget, outcome_current, month_control):
        assert month_control.outcome_variable == 1

    def test_return_from_user_only(
            self, outcome_current, another_user, month_control):
        assert len(month_control.outcome_list) == 1
        outcome_current.user = another_user
        outcome_current.save()
        month_control._prepare_outcome()
        assert len(month_control.outcome_list) == 0
