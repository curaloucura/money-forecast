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

    def test_get_savings_total(self, savings_current, month_control):
        assert month_control.get_savings_totals()['total'] == 1

    def test_get_records_matches_date_of_records(
            self, outcome_future, month_control):
        upcoming_records = month_control.get_upcoming_records()
        assert upcoming_records[0][0] == upcoming_records[0][1].start_date
