import pytz

from django.utils import timezone

class TimezoneMiddleware(object):
    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        # TODO: use timezone for not logged in users  
        if request.user.is_authenticated():
            tzname = request.user.profile.timezone
        else:
            tzname = request.session.get('django_timezone')
            
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()