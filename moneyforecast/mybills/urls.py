from django.conf.urls import patterns, include, url
from django.contrib import admin
from records.views import index, set_language
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'minhascontas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
         name="logout"),
    url(r'^i18n/$', set_language, name='set_language'),
    url(r'^$', index),
)
