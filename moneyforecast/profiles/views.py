from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from .models import Profile
from .forms import ProfileForm
import pytz

def set_timezone(request):
    if request.REQUEST.get('timezone', None):
        request.session['django_timezone'] = request.REQUEST['timezone']

    return redirect(reverse('dashboard'))


class UpdateProfileView(UpdateView):
    model = Profile
    template_name = 'includes/edit_profile_form.html'
    form_class = ProfileForm

    def form_valid(self, form): 
        instance = form.save(commit=False)
        # Make sure the record is owned by the user
        if self.request.user == instance.user:
            instance.save() 

        return HttpResponse('successfully-sent!')


