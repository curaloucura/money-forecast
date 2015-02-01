from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from datetime import datetime, timedelta

OUTCOME = 0
INCOME = 1
SAVINGS = 2
SYSTEM_ACCOUNTS = 3
TYPE_ACCOUNT_CHOICES = ((OUTCOME, _('Outcome')),(INCOME, _('Income')), (SAVINGS, _('Savings')), (SYSTEM_ACCOUNTS, _('System Internals')))

INITIAL_BALANCE_SLUG = 'initial_balance'
UNSCHEDULED_DEBTS_SLUG = 'unscheduled'


class Account(models.Model):
	name = models.CharField(max_length=50)
	type_account = models.IntegerField(choices=TYPE_ACCOUNT_CHOICES)
	slug = models.SlugField(null=True)
	user = models.ForeignKey(User, blank=True, null=True)

	def __unicode__(self):
		return self.name

	# TODO: Prevent from changing the slug from System Accounts


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

	# TODO: on saving System Accounts, make sure invalid fields are not being saved like end_date


@receiver(post_save, sender=User)
def generate_default_accounts(sender, instance, created, **kwargs):
	default_accounts = (
		(_('Salary'),'salary', INCOME),
		(_('Food & Goods'),'food', OUTCOME),
		(_('House Expenses'),'house', OUTCOME),
		(_('Extra Income'),'extra_income', INCOME),
		(_('Extra Outcome'),'extra_outcome', OUTCOME),
		(_('Savings'),'savings', SAVINGS),
		(_('Initial Balance'),INITIAL_BALANCE_SLUG, SYSTEM_ACCOUNTS),
		(_('Unscheduled Debts'),UNSCHEDULED_DEBTS_SLUG, SYSTEM_ACCOUNTS),
	)
	if created:
		# Create default accounts for the new user
		for account in default_accounts:
			Account.objects.create(
				name = account[0],
				slug = account[1],
				type_account = account[2],
				user = instance,
			)

		# Create initial balance for last month, otherwise goes into infinite loop
		Record.objects.create(
			description = _('initial_balance'),
			account = Account.objects.get(slug=INITIAL_BALANCE_SLUG, type_account=SYSTEM_ACCOUNTS, user=instance),
			value = 0,
			start_date = datetime.today(), 
			user = instance
		)
