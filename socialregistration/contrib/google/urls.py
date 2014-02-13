from django.conf import settings
from socialregistration.compat.urls import *
from socialregistration.contrib.google.views import GoogleRedirect, \
    GoogleCallback, GoogleSetup
 
urlpatterns = patterns('',
    url('^redirect/$', GoogleRedirect.as_view(), name='redirect'),
    url('^callback/$', GoogleCallback.as_view(), name='callback'),
    url('^setup/$', GoogleSetup.as_view(), name='setup'),
)
