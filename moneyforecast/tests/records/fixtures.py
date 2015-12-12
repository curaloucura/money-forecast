import pytest
from datetime import datetime, timedelta

from django.contrib.auth.models import User

from records.models import Category, Record, OUTCOME, SAVINGS
from records.month_control import MonthControl


@pytest.fixture
def current_date():
    return datetime.today()


@pytest.fixture
def future_date(current_date):
    date = current_date+timedelta(days=7)
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
    Category of Outcome
    """
    category = Category.objects.create(
        name="outcome", type_category=OUTCOME, user=user)
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
def savings_record(request, user, savings, current_date):
    """
    Record of type Outcome set in the future
    """
    record = Record.objects.create(
        category=savings, amount=1, start_date=current_date, user=user)
    return record
