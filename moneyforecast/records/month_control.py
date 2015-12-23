from datetime import datetime
from decimal import Decimal

from django.db.models import Q, Sum
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

# TODO: move this function to a util module
from records.models import (
    tmz, get_last_date_of_month, Category, Record, INCOME, OUTCOME, SAVINGS,
    SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG, UNSCHEDULED_DEBT_SLUG,
    UNSCHEDULED_CREDIT_SLUG, Budget)


def _cache_key(date):
    return '%d-%d' % (date.month, date.year)


class MonthControl(object):
    def __init__(self, user, month, year, cache=None):
        self.user = user
        self.cache = cache
        self.today = now().replace(hour=0, minute=0)
        budget, created = Budget.objects.get_or_create(
            user=user, category__isnull=True)
        self.budget = budget.amount

        self.set_month_and_year(month, year)

    def __str__(self):
        return "MonthControl for {} / {}".format(self.month, self.year)

    def set_month_and_year(self, month, year):
        self.month = month
        self.year = year
        self.start_date = tmz(datetime(day=1, month=month, year=year))
        # end_date is the last day of the month
        self.end_date = get_last_date_of_month(month, year).replace(
            hour=23, minute=59, second=59)
        self.last_month = (self.start_date-relativedelta(months=1))

        # Initialize variables
        self.initial_balance = Decimal('0')
        self._get_records()
        self._calculate_totals()

    def is_current(self):
        return ((self.today >= self.start_date) and
                (self.today <= self.end_date))

    def _calculate_totals(self):
        self.initial_balance = self.get_initial_balance()
        self._set_income_and_outcome()
        self._set_sum_of_amounts()

        self.total_income = self.income_monthly + self.income_variable
        self.total_outcome = self.outcome_monthly + self.outcome_variable
        self.difference = ((self.income_monthly+self.income_variable) -
                           (self.outcome_monthly+self.outcome_variable))
        self.accountable_difference = (
            (self.accountable_income_monthly +
             self.accountable_income_variable) -
            (self.accountable_outcome_monthly +
             self.accountable_outcome_variable)
            )
        self.final_balance = self.initial_balance + self.accountable_difference

    def _set_income_and_outcome(self):
        # TODO: display total amount but not use it for calculations
        self.income_monthly = sum([x.amount for x in self.income_monthly_list])
        self.income_variable = sum(
            [x.amount for x in self.income_variable_list])
        self.outcome_monthly = sum(
            [x.amount for x in self.outcome_monthly_list])
        outcome_variable = sum(
            [x.amount for x in self.outcome_variable_list])
        self._set_budget_amounts(outcome_variable)
        self.outcome_variable = outcome_variable + self.remaining_budget

    def _set_sum_of_amounts(self):
        self.accountable_income_monthly = self._sum_after_date(
            self.initial_balance_date, self.income_monthly_list)
        self.accountable_income_variable = self._sum_after_date(
            self.initial_balance_date, self.income_variable_list)
        self.accountable_outcome_monthly = self._sum_after_date(
            self.initial_balance_date, self.outcome_monthly_list)
        self.accountable_outcome_variable = self._sum_after_date(
            self.initial_balance_date, self.outcome_variable_list)

    def _sum_after_date(self, date, record_list):
        total = 0
        for record in record_list:
            if record.is_accountable(date):
                total += record.amount

        return total

    def _set_budget_amounts(self, amount_used):
        self.used_budget = min(amount_used, self.budget)
        self.remaining_budget = self.budget - self.used_budget
        self.budget_over_amount = max(amount_used - self.budget, 0)

    def _sort_records_by_date(self, record_list):
        records_for_the_month = []
        for record in record_list:
            # Calculate dates
            records_for_the_month.append(
                (record.get_date_for_month(self.month, self.year), record))

        date_idx = 0
        records_for_the_month.sort(key=lambda r: r[date_idx])
        return records_for_the_month

    def _get_records(self):
        self.income_monthly_list = self._get_records_by_type(INCOME, True)
        self.income_variable_list = self._get_records_by_type(INCOME, False)
        self.outcome_monthly_list = self._get_records_by_type(OUTCOME, True)
        self.outcome_monthly_list = (
            self.outcome_monthly_list + self._get_records_by_type(
                SAVINGS, True))
        self.outcome_variable_list = self._get_records_by_type(OUTCOME, False)
        self.outcome_variable_list = (
            self.outcome_variable_list + self._get_records_by_type(
                SAVINGS, False))
        self.income_list = self.income_monthly_list + self.income_variable_list
        self.sorted_income_list = self._sort_records_by_date(self.income_list)
        self.outcome_list = (
            self.outcome_monthly_list + self.outcome_variable_list)
        self.sorted_outcome_list = self._sort_records_by_date(
            self.outcome_list)

    def _filter_records_not_ended(self, records, date_limit):
        records = records.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=date_limit))
        return records

    def _filter_by_category(self, records, category):
        records = records.filter(category__type_category=category)
        return records

    def _filter_out_child_records(self, records, recurring):
        ignore_day_of_month = not recurring
        records = records.filter(
            parent__isnull=True, day_of_month__isnull=ignore_day_of_month)
        return records

    def _filter_records_starting_this_month(self, records):
        records = records.filter(start_date__gte=self.start_date)
        return records

    def _get_records_by_type(self, category, recurring):
        records = self.get_queryset()
        records = self._filter_records_not_ended(records, self.start_date)
        records = self._filter_by_category(records, category)
        records = self._filter_out_child_records(records, recurring)

        if not recurring:
            records = self._filter_records_starting_this_month(records)
            record_list = list(records)
        else:
            # If recurring, it should check if there's a record for the month
            record_list = []
            for record in records:
                record_list.append(
                    record.get_record_for_month(self.month, self.year))

        return record_list

    def get_queryset(self):
        # Make sure to filter only records by the user
        # TODO: improve the way to track paid off or it could disappear
        # prematurely
        records = Record.objects.filter(user=self.user, is_paid_out=False)

        # All records must start in the month or earlier
        records = records.filter(start_date__lte=self.end_date)

        return records

    def _get_initial_balance_info(self):
        balance = self.get_queryset().filter(
            category__type_category=SYSTEM_CATEGORIES,
            category__slug=INITIAL_BALANCE_SLUG)
        # Initial Balance must be from this month
        balance = balance.filter(start_date__range=(
            self.start_date, self.end_date))
        if balance.count():
            # Get the most recent balance
            idx = balance.count()-1
            return (balance[idx].start_date, balance[idx].amount, balance[idx])
        else:
            if self.cache:
                last_balance = self.cache.get(
                    _cache_key(self.last_month), None)
                if not last_balance:
                    last_balance = MonthControl(
                        self.user, self.last_month.month, self.last_month.year)
                    self.cache[_cache_key(self.last_month)] = last_balance
                final_balance = last_balance.final_balance
            else:
                final_balance = 0
            # If using last month, initial date is the first day of the month
            return (self.start_date, final_balance, None)

    def get_initial_balance(self):
        if not self.initial_balance:
            (self.initial_balance_date,
             self.initial_balance,
             self.initial_balance_instance) = self._get_initial_balance_info()

        return self.initial_balance

    def set_initial_balance(self, amount):
        # TODO: set record for initial balance for the month
        pass

    def get_upcoming_records(self):
        """
        This will return a tuple with the date for the month and the record.
        It is necessary since you can't get the date of a recurring event
        inside the template
        """
        upcoming = []

        for record in self.sorted_outcome_list:
            if record[0] >= self.today:
                upcoming.append(record)
        return upcoming

    def get_savings_totals(self):
        categories = Category.objects.filter(type_category=SAVINGS)
        savings_list = []
        total = 0
        for category in categories:
            total_category = self.get_queryset().filter(
                category=category).aggregate(Sum('amount'))['amount__sum']
            savings_list.append((category, total_category))
            total += (total_category or 0)

        return {'list': savings_list, 'total': total}

    def _get_unscheduled(self, slug_category):
        category = Category.objects.get(
            type_category=SYSTEM_CATEGORIES, slug=slug_category,
            user=self.user)
        records = Record.objects.filter(user=self.user, category=category)
        total = records.aggregate(Sum('amount'))['amount__sum']
        return {'list': records, 'total': total}

    def get_unscheduled_debt_totals(self):
        return self._get_unscheduled(UNSCHEDULED_DEBT_SLUG)

    def get_unscheduled_credit_totals(self):
        return self._get_unscheduled(UNSCHEDULED_CREDIT_SLUG)
