import pytest
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User

from records.models import (
    Category, Record, Budget, OUTCOME, INCOME, SAVINGS, tmz)
from records.month_control import MonthControl, MonthControlWithBudget


@pytest.fixture
def current_date():
    today = date.today()
    today_datetime = datetime(
        day=today.day, month=today.month, year=today.year)
    return tmz(today_datetime)


@pytest.fixture
def future_date(current_date):
    date = current_date+relativedelta(days=1)
    return date


@pytest.fixture
def day_of_month(future_date):
    return future_date.day


@pytest.fixture
def start_of_recurrence(future_date):
    """
    Date object representing the first day of a record with recurrence
    """
    return future_date


@pytest.fixture
def end_of_recurrence(future_date):
    """
    Return a date which is used to determine the end month the recurrence
    should occur
    """
    date = future_date+relativedelta(months=6)
    return date


@pytest.fixture
def next_month(current_date):
    date = current_date+relativedelta(months=1)
    return date


@pytest.fixture
def next_month_future(future_date):
    date = future_date+relativedelta(months=1)
    return date


@pytest.fixture
def infinite_future_date(current_date):
    date = current_date+relativedelta(years=360)
    return date


@pytest.fixture
def month_control(user, current_date):
    """
    Return a MonthControl object for the current date.

    Important: currently any Record fixture should come before month_control
    """
    month_control = MonthControl(
        user, current_date.month, current_date.year, cache={})
    return month_control


@pytest.fixture
def month_control_with_budget(user, current_date):
    """
    Return a MonthControlWithBudget object for the current date.

    Important: currently any Record fixture should come before month_control
    """
    month_control = MonthControlWithBudget(
        user, current_date.month, current_date.year, cache={})
    return month_control


def _user(username='test_user'):
    raw_password = "fake"
    new_user = User.objects.create_user(
        username=username, email="a@b.com", password=raw_password)
    setattr(new_user, "raw_password", raw_password)
    return new_user


@pytest.fixture
def user():
    return _user()


@pytest.fixture
def another_user():
    return _user('another_user')


@pytest.fixture
def outcome(user):
    """
    Main category of outcome type
    """
    category = Category.objects.create(
        name="outcome", type_category=OUTCOME, user=user)
    return category


@pytest.fixture
def income(user):
    """
    Main category of income type
    """
    category = Category.objects.create(
        name="income", type_category=INCOME, user=user)
    return category


@pytest.fixture
def savings(user):
    """
    Category of Savings
    """
    category = Category.objects.create(
        name="savings", type_category=SAVINGS, user=user)
    return category


@pytest.fixture
def outcome_current(user, outcome, current_date):
    """
    Record of type Outcome set to today (current date)
    """
    record = Record.objects.create(
        category=outcome, amount=1, start_date=current_date, user=user)
    return record


@pytest.fixture
def outcome_future(user, outcome, future_date):
    """
    Record of type Outcome set in the future
    """
    record = Record.objects.create(
        category=outcome, amount=1, start_date=future_date, user=user)
    return record


@pytest.fixture
def outcome_recurrent(user, outcome, start_of_recurrence):
    """
    Record of type Outcome set in the future with a day of the month set
    to create a recurring record

    This fixture should not be used with outcome_recurrent_limited and
    outcome_with_parent since they change the instance of this own record
    """
    record = Record.objects.create(
        category=outcome, amount=1, start_date=start_of_recurrence, user=user,
        day_of_month=start_of_recurrence.day)
    return record


@pytest.fixture
def outcome_recurrent_limited(user, outcome_recurrent, end_of_recurrence):
    """
    Record of type Outcome set in the future with a recurring day of the month
    set and limited to a certain time
    """
    outcome_recurrent.end_date = end_of_recurrence
    outcome_recurrent.save()
    return outcome_recurrent


@pytest.fixture
def outcome_with_parent(
        outcome_future, outcome_recurrent, next_month_future):
    outcome_future.parent = outcome_recurrent
    outcome_future.start_date = next_month_future
    outcome_future.save()
    return outcome_future


@pytest.fixture
def savings_current(request, user, savings, current_date):
    """
    Record of type Outcome set in the future
    """
    record = Record.objects.create(
        category=savings, amount=1, start_date=current_date, user=user)
    return record


@pytest.fixture
def budget(user):
    budget = Budget.objects.create(user=user, amount=1)
    return budget
