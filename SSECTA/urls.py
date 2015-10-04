from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout
from django.contrib import admin
from SSECTA import settings
from chelper.views import *
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SSECTA.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout),
    url(r'^accounts/userinfo/$', showuserinfo),
    url(r'^accounts/register/$', reg),
    url(r'^accounts/realauth/$', processrealauth),
    url(r'^help/$', help),
    url(r'^post/$', postentry),
    url(r'^show/$', showentry),
    url(r'^all/$', allentry),
    url(r'^annoy/$', annoyentry),
    url(r'^edit/$', editentry),
    url(r'^delete/$', delentry),
    (r'^photo/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
