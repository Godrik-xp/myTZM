# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from TZM.trainer.views import *

urlpatterns = patterns('',
    (r'^newuser/(?P<persname>\w+)$', newuser),
    (r'^getphoto/(?P<username>\w+)$', getphoto),
    (r'^userlist/$', userlist),

    #(r'^start_sync/(?P<category_id>\d+)/(?P<type_log>\d+)/$', start_sync),
    #(r'^end_sync/(?P<block_id>\d+)/$', end_sync),
    #(r'^sync/(?P<block_id>\d+)/$', sync_log),

    (r'^sync/admin/$', sync_admin),
    url(r'^sync/state/$', sync_state, name='sync_state'),
    (r'^sync/$', sync),
 
    (r'^log/(?P<category_id>\d+)/(?P<type_log>\d+)/(?P<rating>\d+)/$', log),
    (r'^statelist/$', statelist),
    (r'^testlist/$', testslist),
    (r'^testlist/(?P<category_id>\d+)/$', test_by_id),
    (r'^testlist/(?P<category_id>\d+)/(?P<question_count>\d+)/$', test_by_id),
#    (r'^login/$', tzm_login),
	(r'^login/$', login_html),
	(r'^UserPage/$', userPage_html),
	(r'^Test/$', test_html),
	(r'^Results/$', results_html),
    (r'^logout/$', tzm_logout),
	(r'^video/(\d*)/$', show_sample_video),
)
