from django.conf.urls import patterns, include, url
from django.contrib import admin
from records.views import index, set_language, CreateRecordView
from profiles.views import set_timezone
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
         name="logout"),
    url(r'^i18n/$', set_language, name='set_language'),
    url(r'^tz/$', set_language, name='set_language'),
    url(r'^record/create/(?P<type>\d+)/$', CreateRecordView.as_view(), name='create_record'),
    url(r'^record/update/(?P<pk>\d+)/$', CreateRecordView.as_view(), name='update_record'),
    url(r'^$', index, name='dashboard'),
)
