from django import template
from django.utils.safestring import mark_safe
from django.utils import formats
from django.contrib.humanize.templatetags.humanize import intcomma
import math

register = template.Library()

@register.filter
def format_number(amount):
    return "%s%s" % (intcomma(int(amount)), formats.number_format(amount, decimal_pos=2)[-3:])

@register.filter
def pretty_number(amount,variation=None):
    # Change number color except for 0
    sclass = ''
    if amount < 0:
        sclass = 'text-danger'
    elif amount > 0:
        sclass = 'text-success'

    if variation == 'absolute':
        amount = math.fabs(amount)

    return mark_safe('<span class="%s">%s</span>' % (sclass, format_number(amount)))

@register.filter
def date_for_month(record, base_date):
    return record.get_date_for_month(base_date.month, base_date.year)


@register.filter
def is_accountable(record, date):
    return record.is_accountable(date)

