from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

OUTCOME = 0
INCOME = 1
# Savings has it's own category because it must be grouped together
SAVINGS = 2
# System Categories are those not being accounted
SYSTEM_CATEGORIES = 3
TYPE_CATEGORY_CHOICES = (
    (OUTCOME, _('Outcome')), (INCOME, _('Income')), (SAVINGS, _('Savings')),
    (SYSTEM_CATEGORIES, _('System Internals')))

INITIAL_BALANCE_SLUG = 'initial_balance'
UNSCHEDULED_DEBT_SLUG = 'unscheduled_debt'
UNSCHEDULED_CREDIT_SLUG = 'unscheduled_credit'


class Category(models.Model):
    name = models.CharField(max_length=50)
    type_category = models.IntegerField(choices=TYPE_CATEGORY_CHOICES)
    slug = models.SlugField(null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('type_category', 'name')
        verbose_name_plural = _('Categories')

    # TODO: Prevent from changing the slug from System Categories


def tmz(naive_date):
    return timezone.make_aware(naive_date)


def get_last_date_of_month(month, year):
    first_date_of_the_month = datetime(day=1, month=month, year=year)
    first_date_of_next_month = first_date_of_the_month+relativedelta(months=1)
    last_date_of_the_month = first_date_of_next_month-timedelta(days=1)
    return tmz(last_date_of_the_month)


class Record(models.Model):
    description = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(Category, help_text=_(
        'Select the category for this record. This field is required'))
    amount = models.FloatField(
        default=0, verbose_name=_("How much?"),
        help_text=_(
            "Please, use only the monthly amount. This field is required"))
    start_date = models.DateTimeField(
        default=timezone.now, verbose_name=_('Date'),
        help_text=_('This field is required'))
    day_of_month = models.SmallIntegerField(
        blank=True, null=True, verbose_name=_("Day of the month"),
        help_text=_(
            'Use this field to set recurring bills. '
            'The day in which will you be billed every month'))
    number_payments = models.SmallIntegerField(
        blank=True, null=True, verbose_name=_("Number of Payments"),
        help_text=_('This is only used to generate the final payment date'))
    end_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_('Last payment on'),
        help_text=_(
            'This is the date when it will be the last payment for this '
            'record, after this date the record will not appear '
            'on the calculations'))
    is_paid_out = models.BooleanField(
        default=False, verbose_name=_('Is it totally paid?'),
        help_text=_(
            'If checked, the record won\'t appear in the '
            'calculations anymore. Click it only to hide a record '
            'from your spreadsheet'))
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return "%s %s %s" % (self.description, self.category, self.amount)

    def get_date_for_month(self, month, year):
        """
        Get date for the record, but when it's recurring, will get
        the date object for the month using the day_of_month
        For recurring objects, month and year are required
        """
        record = self.get_record_for_month(month, year)

        if record._is_same_month_and_year(month, year):
            date = record.start_date
        else:
            date = record._get_date_of_month_on(month, year)

        return date

    def _is_same_month_and_year(self, month, year):
        local_start = timezone.localtime(self.start_date)
        same_month = month == local_start.month
        same_year = year == local_start.year
        return same_month and same_year

    def _get_date_of_month_on(self, month, year):
        day = self._get_valid_day_of_month(month, year)
        return tmz(datetime(day=day, month=month, year=year))

    def _get_valid_day_of_month(self, month, year):
        day = self.day_of_month
        if not(day in range(1, 32)):
            raise ValueError(
                "Day of month invalid. It must be an integer between 1 and 31")

        # Avoid returning 31 of February for example
        last_day = get_last_date_of_month(month, year)
        if self.day_of_month > last_day.day:
            day = last_day.day

        return day

    def is_accountable(self, on_date=None):
        """
        An accountable record is all records that are in the same day or
        after the initial balance for the month
        """
        # TODO: Perhaps consider checking the time too?
        record_date = self.get_date_for_month(
            on_date.month, on_date.year)
        return on_date <= record_date

    def get_default_description(self):
        return self.description or self.category.name

    # TODO: on saving System Categories, make sure invalid fields
    # are not being saved like end_date
    def is_savings(self):
        return self.category.type_category == SAVINGS

    def is_recurrent(self):
        return (self.day_of_month is not None) and (self.day_of_month > 0)

    def _in_range_of_recurrence(self, date):
        if self.parent:
            recurrent = self.parent
        else:
            recurrent = self

        start_range = recurrent.start_date <= date
        end_range = True
        if recurrent.end_date:
            end_range = recurrent.end_date >= date
        return start_range and end_range

    def _get_default_recurrent_record(self, month, year):
        day = self._get_valid_day_of_month(month, year)
        record_date_for_month = datetime(day=day, month=month, year=year)
        if self._in_range_of_recurrence(tmz(record_date_for_month)):
            default_record = self
        else:
            raise OutOfRange("{}/{} is not a valid date for record {}".format(
                month, year, self))
        return default_record

    def get_record_for_month(self, month, year):
        if self.is_recurrent():
            record = self._get_record_for_recurrent(month, year)
        else:
            record = self._get_record_for_non_recurrent(month, year)
        return record

    def _get_record_for_recurrent(self, month, year):
        default_record = self._get_default_recurrent_record(month, year)

        record = self._get_other_record_on(month, year)
        if not record:
            record = default_record
        return record

    def _get_record_for_non_recurrent(self, month, year):
        if self._is_same_month_and_year(month, year):
            record = self
        else:
            record = None
        return record

    def _get_other_record_on(self, month, year):
        record_at_date = Record.objects.filter(
            parent=self, start_date__month=month, start_date__year=year)
        if record_at_date.count():
            record = record_at_date[0]
        else:
            record = None
        return record


class OutOfRange(ValueError):
    pass


@receiver(post_save, sender=User)
def generate_default_categories(sender, instance, created, **kwargs):
    default_categories = (
        (_('Salary'), 'salary', INCOME),
        (_('Food & Goods'), 'food', OUTCOME),
        (_('House Expenses'), 'house', OUTCOME),
        (_('Extra Income'), 'extra_income', INCOME),
        (_('Extra Outcome'), 'extra_outcome', OUTCOME),
        (_('Savings'), 'savings', SAVINGS),
        (_('Monthly Balance'), INITIAL_BALANCE_SLUG, SYSTEM_CATEGORIES),
        (_('Unscheduled Debts'), UNSCHEDULED_DEBT_SLUG, SYSTEM_CATEGORIES),
        (_('Unscheduled Credit'), UNSCHEDULED_CREDIT_SLUG, SYSTEM_CATEGORIES),
    )
    if created:
        # Create default categories for the new user
        for category in default_categories:
            Category.objects.create(
                name=category[0],
                slug=category[1],
                type_category=category[2],
                user=instance,
            )

        # Create initial balance for last month,
        # otherwise goes into infinite loop
        Record.objects.create(
            description=_('Initial Balance'),
            category=Category.objects.get(
                slug=INITIAL_BALANCE_SLUG, type_category=SYSTEM_CATEGORIES,
                user=instance),
            amount=0,
            start_date=timezone.now().replace(day=1),
            user=instance
        )
