from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from records.models import Record, INCOME, OUTCOME, SAVINGS, SYSTEM_ACCOUNTS, INITIAL_BALANCE_SLUG

class MonthControl(object):
	def __init__(self, user, month, year):
		self.user = user
		self.start_date = date(day=1, month=month, year=year)
		# end_date is the last day of the month
		self.end_date = (self.start_date+relativedelta(months=1))-timedelta(days=1)
		self.last_month = (self.start_date-relativedelta(months=1))
		self._get_records()
		self._calculate_totals()

	def _calculate_totals(self):
		self.initial_balance = self.get_initial_balance()
		self.income_monthly = sum([x.value for x in self.income_monthly_list])
		self.income_variable = sum([x.value for x in self.income_variable_list])
		self.outcome_monthly = sum([x.value for x in self.outcome_monthly_list])
		self.outcome_variable = sum([x.value for x in self.outcome_variable_list])
		self.total_income = self.income_monthly + self.income_variable
		self.total_outcome = self.outcome_monthly + self.outcome_variable
		self.difference = ((self.income_monthly+self.income_variable) -
						 	(self.outcome_monthly+self.outcome_variable))
		self.final_balance = self.initial_balance + self.difference

	def _get_records(self):
		self.income_monthly_list = self._get_records_by_type(INCOME, False)
		self.income_variable_list = self._get_records_by_type(INCOME, True)
		self.outcome_monthly_list = self._get_records_by_type(OUTCOME, False)
		self.outcome_variable_list = self._get_records_by_type(OUTCOME, True)

	def _get_records_by_type(self, account, one_time_only):
		records = self.get_queryset().filter(is_paid_off=False) # TODO: improve the way to track paid off or it could disappear prematurely
		records = records.filter( Q(end_date__isnull=True) | Q(end_date__range=(self.start_date, self.end_date)) )
		records = records.filter(account__type_account=account, day_of_month__isnull=one_time_only)

		if one_time_only:
			# If not recurring, then it should check the start date
			records = records.filter(start_date__range=(self.start_date, self.end_date))
		return records

	def get_queryset(self):
		# Make sure to filter only records by the user
		records = Record.objects.filter(user=self.user) 

		# All records must start in the month or earlier
		records = records.filter(start_date__lte=self.end_date)
		
		return records

	def get_initial_balance(self):
		balance = self.get_queryset().filter(account__type_account=SYSTEM_ACCOUNTS, account__slug=INITIAL_BALANCE_SLUG) 
		# Initial Balance must be from this month
		balance = balance.filter(start_date__range=(self.start_date, self.end_date))
		if balance.count():
			return balance[0].value
		else:
			# TODO: Have to improve it, raising errors when no last balance is found
			last_balance = MonthControl(self.user, self.last_month.month, self.last_month.year)
			return last_balance.final_balance

	def set_initial_balance(self, value):
		# TODO: set record for initial balance for the month
		pass

	def get_upcoming_records(self):
		# TODO: this have to bring all records from today until end of the month, recurring and one-timer bills
		pass


@login_required
def index(request):
	month_list = []
	today = datetime.today()
	for i in range(0,11):
		target_month = today+relativedelta(months=i)
		month_list.append(MonthControl(request.user, target_month.month, target_month.year))

	current_month = month_list[0]
	return render(request, "base.html", locals())
