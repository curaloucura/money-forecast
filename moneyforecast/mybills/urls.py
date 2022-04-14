from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from records.views import index, set_language, CreateRecordView, UpdateRecordView,\
         DeleteRecordView, UpdateInitialBalanceView, CreateInitialBalanceView,\
         CreateUnscheduledDebtView, CreateUnscheduledCreditView, UpdateUnscheduledDebtView,\
         UpdateUnscheduledCreditView, CreateRecurrentMonthView, EditRecurrentMonthView
from profiles.views import set_timezone, UpdateProfileView
from django.urls import reverse_lazy

urlpatterns = [ 
    path('admin/', admin.site.urls),
    # User general
    re_path(r'^logout/$', auth_views.LogoutView.as_view(),
         name="logout"),
    re_path(r'^i18n/$', set_language, name='set_language'),
    re_path(r'^tz/$', set_language, name='set_language'),
    re_path(r'^profile/update/(?P<pk>\d+)/$', UpdateProfileView.as_view(), name='update_profile'),

    # Records
    re_path(r'^record/create/(?P<type>\d+)/$', CreateRecordView.as_view(), name='create_record'),
    re_path(r'^record/update/(?P<pk>\d+)/$', UpdateRecordView.as_view(), name='update_record'),
    re_path(r'^record/delete/(?P<pk>\d+)/$', DeleteRecordView.as_view(), name='delete_record'),
    re_path(r'^record/recurrent/create/(?P<parent_pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', CreateRecurrentMonthView.as_view(), name='create_recurrent_month'),
    re_path(r'^record/recurrent/edit/(?P<pk>\d+)/$', EditRecurrentMonthView.as_view(), name='edit_recurrent_month'),

    # System accounts
    re_path(r'^balance/create/$', CreateInitialBalanceView.as_view(), name='create_initial_balance'),
    re_path(r'^balance/update/(?P<pk>\d+)/$', UpdateInitialBalanceView.as_view(), name='update_initial_balance'),
    re_path(r'^u_debt/create/$', CreateUnscheduledDebtView.as_view(), name='create_unscheduled_debt'),
    re_path(r'^u_debt/update/(?P<pk>\d+)/$', UpdateUnscheduledDebtView.as_view(), name='update_unscheduled_debt'),
    re_path(r'^u_credit/create/$', CreateUnscheduledCreditView.as_view(), name='create_unscheduled_credit'),
    re_path(r'^u_credit/update/(?P<pk>\d+)/$', UpdateUnscheduledCreditView.as_view(), name='update_unscheduled_credit'),

    #Dashboard
    re_path(r'^$', index, name='dashboard'),
]
