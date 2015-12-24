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

    def test_one_month_before_end_date_is_displayed(
            self, outcome_recurrent_limited, month_control, end_of_recurrence):
        one_month_before = end_of_recurrence - relativedelta(months=1)
        month_control.set_month_and_year(
            one_month_before.month, one_month_before.year)
        records = month_control.outcome_list
        assert records[0] == outcome_recurrent_limited

    def test_recurring_day_has_no_past_records(
            self, outcome_recurrent, start_of_recurrence, month_control):
        past_date = start_of_recurrence - relativedelta(months=1)
        month_control.set_month_and_year(past_date.month, past_date.year)
        records = month_control.get_upcoming_records()
        assert len(records) == 0

    def test_recurring_with_other_other_is_returned(
            self, outcome_with_parent, outcome_recurrent, next_month_future,
            month_control):

        date = next_month_future
        month_control.set_month_and_year(date.month, date.year)
        records = month_control.get_upcoming_records()
        record_other = records[0][1]
        assert record_other == outcome_with_parent
