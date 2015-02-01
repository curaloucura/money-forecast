from django.shortcuts import render
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from records.models import Record, INCOME, OUTCOME, SAVINGS, SYSTEM_ACCOUNTS, INITIAL_BALANCE_ID

class MonthControl(object):
	def __init__(self, month, year):
		self.start_date = date(day=1, month=month, year=year)
		self.end_date = (self.start_date+relativedelta(months=1))-timedelta(days=1)
		self._get_records()
		self._calculate_totals()

	def _calculate_totals(self):
		self.income_monthly = sum([x.value for x in self.income_monthly_list])
		self.income_variable = sum([x.value for x in self.income_variable_list])
		self.outcome_monthly = sum([x.value for x in self.outcome_monthly_list])
		self.outcome_variable = sum([x.value for x in self.outcome_variable_list])

	def _get_records(self):
		self.income_monthly_list = self._get_records_by_type(INCOME, False)
		self.income_variable_list = self._get_records_by_type(INCOME, True)
		self.outcome_monthly_list = self._get_records_by_type(OUTCOME, False)
		self.outcome_variable_list = self._get_records_by_type(OUTCOME, True)

	def _get_records_by_type(self, account, one_time_only):
		records = Record.objects.filter(is_paid_off=False) # TODO: improve the way to track paid off or it could disappear prematurely
		records = Record.objects.filter(start_date__range=(self.start_date, self.end_date))
		records = records.filter( Q(end_date__isnull=True) | Q(end_date__range=(self.start_date, self.end_date)) )
		records = records.filter(account__type_account=account, day_of_month__isnull=one_time_only)
		# TODO: make recurrent events to always appear on the list
		return records

	@property
	def initial_balance(self):
		balance = Record.objects.filter(account__type_account=SYSTEM_ACCOUNTS, account__id=INITIAL_BALANCE_ID) 
		balance = balance.filter(start_date__range=(self.start_date, self.end_date))
		if balance.count():
			return balance[0].value
		else:
			return 0 # TODO: have to try to get balance from last month	

	@initial_balance.setter
	def set_initial_balance(self, value):
		pass



def index(request):
	month_list = []
	today = datetime.today()
	for i in range(0,5):
		target_month = today+relativedelta(months=i)
		month_list.append(MonthControl(target_month.month, target_month.year))

	return render(request, "base.html", locals())
