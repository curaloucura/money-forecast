from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime

OUTCOME = 0
INCOME = 1
SAVINGS = 2
SYSTEM_ACCOUNTS = 3
TYPE_ACCOUNT_CHOICES = ((OUTCOME, _('Outcome')),(INCOME, _('Income')), (SAVINGS, _('Savings')), (SYSTEM_ACCOUNTS, _('System Internals')))

INITIAL_BALANCE_ID = 4

class Account(models.Model):
	name = models.CharField(max_length=50)
	type_account = models.IntegerField(choices=TYPE_ACCOUNT_CHOICES)
	user = models.ForeignKey(User, blank=True, null=True)

	def __unicode__(self):
		return self.name


class Record(models.Model):
	description = models.CharField(max_length=50, blank=True)
	account = models.ForeignKey(Account)
	value = models.FloatField(default=0, help_text=_("Please, use only the monthly value"))
	day_of_month = models.SmallIntegerField(blank=True, null=True, help_text=_('Use este campo para contas mensais'))
	number_payments = models.SmallIntegerField(blank=True, null=True)
	start_date = models.DateField(default=datetime.today)
	end_date = models.DateField(blank=True, null=True)
	is_paid_off = models.BooleanField(default=False)
	notes = models.TextField(blank=True, null=True)
	user = models.ForeignKey(User, blank=True, null=True)
	
	def __unicode__(self):
		return "%s %s %s" % (self.description,self.account,self.value)