import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User

from records.models import Category, Record, OUTCOME, INCOME, SAVINGS
from records.month_control import MonthControl


@pytest.fixture
def current_date():
    return datetime.today()


@pytest.fixture
def future_date(current_date):
    date = current_date+relativedelta(days=7)
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
        user, current_date.month, current_date.year, cache=False)
    return month_control


@pytest.fixture
def user(request):
    raw_password = "fake"
    new_user = User.objects.create_user(
        username="test_user", email="a@b.com", password=raw_password)
    setattr(new_user, "raw_password", raw_password)
    return new_user


@pytest.fixture
def outcome(request, user):
    """
    Main category of outcome type
    """
    category = Category.objects.create(
        name="outcome", type_category=OUTCOME, user=user)
    return category


@pytest.fixture
def income(request, user):
    """
    Main category of income type
    """
    category = Category.objects.create(
        name="income", type_category=INCOME, user=user)
    return category


@pytest.fixture
def savings(request, user):
    """
    Category of Savings
    """
    category = Category.objects.create(
        name="savings", type_category=SAVINGS, user=user)
    return category


@pytest.fixture
def outcome_future(request, user, outcome, future_date):
    """
    Record of type Outcome set in the future
    """
    record = Record.objects.create(
        category=outcome, amount=1, start_date=future_date, user=user)
    return record


@pytest.fixture
def outcome_recurrent(request, user, outcome, start_of_recurrence):
    """
    Record of type Outcome set in the future with a day of the month set
    to create a recurring record
    """
    record = Record.objects.create(
        category=outcome, amount=1, start_date=start_of_recurrence, user=user,
        day_of_month=start_of_recurrence.day)
    return record


@pytest.fixture
def outcome_recurrent_limited(
        request, user, outcome_recurrent, end_of_recurrence):
    """
    Record of type Outcome set in the future with a recurring day of the month
    set and limited to a certain time
    """
    outcome_recurrent.end_date = end_of_recurrence
    outcome_recurrent.save()
    return outcome_recurrent


@pytest.fixture
def savings_current(request, user, savings, current_date):
    """
    Record of type Outcome set in the future
    """
    record = Record.objects.create(
        category=savings, amount=1, start_date=current_date, user=user)
    return record
