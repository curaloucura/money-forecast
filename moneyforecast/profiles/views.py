from django.shortcuts import render
from django.core.urlresolvers import reverse
import pytz

def set_timezone(request):
    if request.REQUEST.get('timezone', None):
        request.session['django_timezone'] = request.REQUEST['timezone']

    return redirect(reverse('dashboard'))
    # TODO: Page to select timezone
    #else:
    #    return render(request, 'template.html', {'timezones': pytz.common_timezones})
