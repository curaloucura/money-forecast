from django import template
from django.utils.safestring import mark_safe
from django.utils import formats
import math

register = template.Library()


@register.filter
def format_number(amount):
    return formats.number_format(
        amount, decimal_pos=2, use_l10n=True, force_grouping=True)


@register.filter
def pretty_number(amount, variation=None):
    # Change number color except for 0
    sclass = ''
    if amount < 0:
        sclass = 'text-danger'
    elif amount > 0:
        sclass = 'text-success'

    if variation == 'absolute':
        amount = math.fabs(amount)

    return mark_safe(
        '<span class="%s">%s</span>' % (sclass, format_number(amount)))


@register.simple_tag
def get_decimal_separator():
    return formats.get_format('DECIMAL_SEPARATOR', use_l10n=True)


@register.simple_tag
def get_thousand_separator():
    return formats.get_format('THOUSAND_SEPARATOR', use_l10n=True)


@register.filter
def date_for_month(record, base_date):
    return record.get_date_for_month(base_date.month, base_date.year)


@register.filter
def is_accountable(record, date):
    return record.is_accountable(date)


@register.simple_tag(takes_context=True)
def is_same_month(context, record, month, year, var_name):
    same_month = (record.start_date.month == month) and (record.start_date.year == year)
    context[var_name] = same_month
    return ""
