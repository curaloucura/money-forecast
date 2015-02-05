from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime, date, timedelta
import pytz
from dateutil.relativedelta import relativedelta

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


def get_last_day_of_month(month, year):
    start_date = datetime(day=1, month=month, year=year)
    start_date = (start_date+relativedelta(months=1))-timedelta(days=1)
    return start_date.replace(tzinfo = pytz.utc)


class Record(models.Model):
    description = models.CharField(max_length=50, blank=True)
    account = models.ForeignKey(Account, help_text=_('Select the account for this record. This field is required'))
    value = models.FloatField(default=0, verbose_name=_("How much?"),help_text=_("Please, use only the monthly amount. This field is required"))
    start_date = models.DateTimeField(default=timezone.now, verbose_name=_('Date'), help_text=_('This field is required'))
    day_of_month = models.SmallIntegerField(blank=True, null=True, verbose_name=_("Day of the month"), help_text=_('Use this field to set recurring bills. The day in which will you be billed every month'))
    number_payments = models.SmallIntegerField(blank=True, null=True, verbose_name=_("Number of Payments"), help_text=_('This is only used to generate the final payment date'))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Last payment on'), help_text=_('This is the date when it will be the last payment for this record, after this date the record will not appear on the calculations'))
    is_paid_out = models.BooleanField(default=False, verbose_name=_('Is it totally paid?'), help_text=_('If checked, the record won\'t appear in the calculations anymore. Click it only to hide a record from your spreadsheet'))
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    
    def __unicode__(self):
        return "%s %s %s" % (self.description,self.account,self.value)

    def _get_valid_date_of_month(self, month, year):
        day = 1
        if self.day_of_month:
            if not(self.day_of_month in range(1,32)):
                # Invalid day, return 1
                day = 1

            # Avoid returning 31 of February for example
            last_day = get_last_day_of_month(month, year)
            if self.day_of_month > last_day.day:
                day = last_day.day
            else:
                day = self.day_of_month

        return date(day=day, month=month, year=year)

    def get_date_for_month(self, month=None, year=None):
        """
        Get date for the record, but when it's recurring, will get the date object for the month using the day_of_month
        For recurring objects, month and year are required
        """

        # Check if parameters are given, then if it's not
        # current month and finally if there is a day of the month
        if month and year:
            if (((month != self.start_date.month) or
                    (month == self.start_date.month) and (year != self.start_date.year))
                and
                    self.day_of_month):
                return self._get_valid_date_of_month(month, year)

        return self.start_date


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
        (_('Monthly Balance'),INITIAL_BALANCE_SLUG, SYSTEM_ACCOUNTS),
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
            start_date = timezone.now(), 
            user = instance
        )
