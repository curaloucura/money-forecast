import pytest
from dateutil.relativedelta import relativedelta


pytest_plugins = ['tests.records.fixtures']


@pytest.mark.django_db
class TestMonthControlRecurrent:
    def test_recurring_day_is_infinite(
            self, outcome_recurrent, infinite_future_date,
            day_of_month, month_control):
        date = infinite_future_date
        month_control.set_month_and_year(date.month, date.year)
        records = month_control.get_upcoming_records()
        only_record_on_the_day = records[0][1]
        assert only_record_on_the_day.day_of_month == day_of_month

    def test_recurring_day_with_end_date_is_returned(
            self, outcome_recurrent_limited, month_control, end_of_recurrence):
        date = end_of_recurrence
        month_control.set_month_and_year(date.month, date.year)
        records = month_control.get_upcoming_records()
        assert len(records) == 1

    def test_after_end_date_nothing_is_returned(
            self, outcome_recurrent_limited, month_control, end_of_recurrence):
        date = end_of_recurrence + relativedelta(months=1)
        month_control.set_month_and_year(date.month, date.year)
        records = month_control.get_upcoming_records()
        assert len(records) == 0

    def test_recurring_day_has_no_past_records(
            self, outcome_recurrent, start_of_recurrence, month_control):
        past_date = start_of_recurrence - relativedelta(months=1)
        month_control.set_month_and_year(past_date.month, past_date.year)
        records = month_control.get_upcoming_records()
        assert len(records) == 0

    @pytest.mark.xfail
    def test_recurring_day_change_on_future_record(self, month_control):
        assert 0

    @pytest.mark.xfail
    def test_recurring_day_change_original_and_future_record(
            self, month_control):
        assert 0
