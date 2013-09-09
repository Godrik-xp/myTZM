# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^async/', include('TZM.async.urls')),
    (r'^trainer/', include('TZM.trainer.urls')),
    ('^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
 {'document_root': settings.MEDIA_ROOT}),
        
   )
