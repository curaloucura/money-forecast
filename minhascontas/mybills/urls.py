from django.conf.urls import patterns, include, url
from django.contrib import admin
from records.views import index

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'minhascontas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
)
