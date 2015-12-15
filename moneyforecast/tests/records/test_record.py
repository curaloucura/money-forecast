import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from records.models import get_last_date_of_month, Record, OutOfRange


pytest_plugins = ['tests.records.fixtures']


def test_get_last_day_of_month():
    known_date_with_ending_day_31 = datetime(day=15, month=12, year=2015)
    date = known_date_with_ending_day_31
    last_day = get_last_date_of_month(date.month, date.year)
    assert last_day.day == 31


@pytest.mark.django_db
class TestRecord:
    @pytest.fixture
    def record(self, user, outcome, future_date):
        record = Record.objects.create(
            category=outcome, user=user, start_date=future_date)
        return record

    @pytest.fixture
    def record_recurrent(self, record, start_of_recurrence):
        record.start_date = start_of_recurrence
        record.day_of_month = start_of_recurrence.day
        record.save()
        return record

    @pytest.fixture
    def record_other(self, user, outcome, record_recurrent, next_month_future):
        other = Record.objects.create(
            category=outcome, user=user, start_date=next_month_future,
            parent=record_recurrent)
        return other

    def test_get_date_for_month_non_recurring_same_month(
            self, record, future_date):
        date = record.get_date_for_month(future_date.month, future_date.year)
        assert date == future_date

    def test_get_date_for_month_recurring_same_month(
            self, record_recurrent, start_of_recurrence):
        date = record_recurrent.get_date_for_month(
            start_of_recurrence.month, start_of_recurrence.year)
        assert date == start_of_recurrence

    def test_get_date_for_month_recurring_is_next_month(
            self, record_recurrent, next_month_future, future_date):
        month = next_month_future
        date = record_recurrent.get_date_for_month(month.month, month.year)
        next_month_date = future_date + relativedelta(months=1)
        assert date == next_month_date

    def test_is_accountable(self, record, future_date):
        initial_balance_entry_date = future_date
        accountable = record.is_accountable(initial_balance_entry_date)
        assert accountable

    def test_is_not_accountable(self, record, future_date):
        initial_balance_entry_date = future_date+relativedelta(days=1)
        accountable = record.is_accountable(initial_balance_entry_date)
        assert not accountable

    def test_description_is_set(self, record):
        record.description = 'is_set'
        assert record.get_default_description() == 'is_set'

    def test_description_is_not_set_get_category_name_instead(
            self, record, outcome):
        record.description = ''
        category = outcome.name
        assert record.get_default_description() == category

    def test_is_savings(self, record, savings):
        record.category = savings
        assert record.is_savings()

    def test_is_not_savings(self, record, outcome):
        record.category = outcome
        assert not record.is_savings()

    def test_is_recurrent(self, record_recurrent):
        assert record_recurrent.is_recurrent()

    def test_is_not_recurrent(self, record):
        assert not record.is_recurrent()

    def test_get_self_as_record_for_current_month(
            self, record_recurrent, start_of_recurrence):
        date = start_of_recurrence
        record_on_month = record_recurrent.get_record_for_month(
            date.month, date.year)
        assert record_on_month == record_recurrent

    def test_get_self_as_record_for_next_month(
            self, record_recurrent, next_month_future):
        date = next_month_future
        record_on_month = record_recurrent.get_record_for_month(
            date.month, date.year)
        assert record_on_month == record_recurrent

    def test_get_other_for_next_month_when_exists(
            self, record_recurrent, record_other, next_month_future):
        date = next_month_future
        record_on_month = record_recurrent.get_record_for_month(
            date.month, date.year)
        assert record_on_month == record_other
        assert record_on_month.parent == record_recurrent

    def test_get_none_if_not_in_range_non_recurrent(
            self, record, next_month_future):
        date = next_month_future
        record_on = record._get_record_for_non_recurrent(
            date.month, date.year)
        assert record_on is None

    def test_get_none_if_not_in_range_recurrent(
            self, record_recurrent, next_month_future, infinite_future_date):
        record_recurrent.end_date = next_month_future
        date = infinite_future_date
        assert not record_recurrent._in_range_of_recurrence(date)
        with pytest.raises(OutOfRange):
            record_on = record_recurrent._get_record_for_recurrent(
                date.month, date.year)

    def test_get_valid_day_of_month_sets_correct_end_date(
            self, record_recurrent):
        record_recurrent.day_of_month = 31
        day_for_february = record_recurrent._get_valid_day_of_month(02, 2015)
        assert day_for_february == 28

    def test_get_valid_day_of_month_raises_exception_on_invalid_date(
            self, record_recurrent):
        record_recurrent.day_of_month = 32
        with pytest.raises(ValueError):
            record_recurrent._get_valid_day_of_month(12, 2015)
