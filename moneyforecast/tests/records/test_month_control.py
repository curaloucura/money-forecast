from datetime import datetime, timedelta
import pytest

from django.contrib.auth.models import User

from records.models import Category, Record, OUTCOME, SAVINGS
from records.month_control import MonthControl


@pytest.fixture
def month_control(user):
    current = datetime.today()
    month_control = MonthControl(
        user, current.month, current.year, cache=False)
    return month_control


@pytest.fixture
def user(request):
    new_user = User.objects.create_user(username="test_user", email="a@b.com")
    return new_user


@pytest.fixture
def outcome(request):
    category = Category.objects.create(
        name="outcome", type_category=OUTCOME)
    return category


@pytest.fixture
def savings(request):
    category = Category.objects.create(
        name="savings", type_category=SAVINGS)
    return category


@pytest.fixture
def outcome_future(request, user, outcome):
    # TODO: a catch, outcome_future must come before month_control
    today = datetime.now()
    day_in_the_future = today + timedelta(days=5)
    record = Record.objects.create(
        category=outcome, amount=1, start_date=day_in_the_future, user=user)
    return record


@pytest.fixture
def savings_record(request, user, savings):
    # TODO: a catch, outcome_future must come before month_control
    today = datetime.now()
    record = Record.objects.create(
        category=savings, amount=1, start_date=today, user=user)
    return record


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

    def test_get_savings_total(self, savings_record, month_control):
        assert month_control.get_savings_totals()['total'] == 1
