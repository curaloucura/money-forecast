from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def pretty_number(value):
	# Change number color except for 0
	sclass = ''
	if value < 0:
		sclass = 'text-danger'
	elif value > 0:
		sclass = 'text-success'

	return mark_safe('<span class="%s">%.2f</span>' % (sclass, value))
