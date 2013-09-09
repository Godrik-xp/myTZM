# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from TZM.async.views import *

urlpatterns = patterns('',
    (r'^start/$', start_async),
    (r'^(?P<id>\d+)/$', async),
)
