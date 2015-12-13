import pytest
from datetime import datetime

from records.models import get_last_date_of_month, Record


def test_get_last_day_of_month():
    known_date_with_ending_day_31 = datetime(day=15, month=12, year=2015)
    date = known_date_with_ending_day_31
    last_day = get_last_date_of_month(date.month, date.year)
    assert last_day.day == 31


@pytest.mark.django_db
class TestRecord:
    def test_get_date_for_month(self):
        assert 0

    def test_is_accountable(self):
        assert 0

    def test_is_not_accountable(self):
        assert 0

    def test_description_is_set(self):
        assert 0

    def test_description_is_not_set_get_category_name_instead(self):
        assert 0

    def test_is_savings(self):
        assert 0

    def test_is_not_savings(self):
        assert 0

    def test_is_recurrent(self):
        assert 0

    def test_is_not_recurrent(self):
        assert 0

    def test_get_record_for_month_and_year(self):
        assert 0
