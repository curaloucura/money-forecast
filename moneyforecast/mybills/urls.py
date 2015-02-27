from django.conf.urls import patterns, include, url
from django.contrib import admin
from records.views import index, set_language, CreateRecordView, UpdateRecordView,\
         DeleteRecordView, UpdateInitialBalanceView, CreateInitialBalanceView,\
         CreateUnscheduledDebtView, CreateUnscheduledCreditView, UpdateUnscheduledDebtView,\
         UpdateUnscheduledCreditView, CreateRecurrentMonthView, EditRecurrentMonthView
from profiles.views import set_timezone, UpdateProfileView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # User general
    url(r'^logout/$', 'django.contrib.auth.views.logout',
         name="logout"),
    url(r'^i18n/$', set_language, name='set_language'),
    url(r'^tz/$', set_language, name='set_language'),
    url(r'^profile/update/(?P<pk>\d+)/$', UpdateProfileView.as_view(), name='update_profile'),

    # Records
    url(r'^record/create/(?P<type>\d+)/$', CreateRecordView.as_view(), name='create_record'),
    url(r'^record/update/(?P<pk>\d+)/$', UpdateRecordView.as_view(), name='update_record'),
    url(r'^record/delete/(?P<pk>\d+)/$', DeleteRecordView.as_view(), name='delete_record'),
    url(r'^record/recurrent/create/(?P<parent_pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', CreateRecurrentMonthView.as_view(), name='create_recurrent_month'),
    url(r'^record/recurrent/edit/(?P<pk>\d+)/$', EditRecurrentMonthView.as_view(), name='edit_recurrent_month'),

    # System accounts
    url(r'^balance/create/$', CreateInitialBalanceView.as_view(), name='create_initial_balance'),
    url(r'^balance/update/(?P<pk>\d+)/$', UpdateInitialBalanceView.as_view(), name='update_initial_balance'),
    url(r'^u_debt/create/$', CreateUnscheduledDebtView.as_view(), name='create_unscheduled_debt'),
    url(r'^u_debt/update/(?P<pk>\d+)/$', UpdateUnscheduledDebtView.as_view(), name='update_unscheduled_debt'),
    url(r'^u_credit/create/$', CreateUnscheduledCreditView.as_view(), name='create_unscheduled_credit'),
    url(r'^u_credit/update/(?P<pk>\d+)/$', UpdateUnscheduledCreditView.as_view(), name='update_unscheduled_credit'),

    #Dashboard
    url(r'^$', index, name='dashboard'),
)
