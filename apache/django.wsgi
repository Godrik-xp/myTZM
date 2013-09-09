import os, sys

sys.path.append('/var/www/')
sys.path.append('/var/www/TZM')
sys.path.append('/var/www/TZM/trainer')

os.environ['DJANGO_SETTINGS_MODULE'] = 'TZM.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
