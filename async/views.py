# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command

from TZM.async.models import *


def start_async(request):
    task_data = request.POST.get('task_data') or request.GET.get('task_data')
    task_name = request.POST.get('task_name') or request.GET.get('task_name')
    if task_name and task_data:
        task = AsyncTask.objects.create(data=task_data)
        call_command('gearman_submit_job', task_name, str(task.id))
        return HttpResponse(task.id)
    else:
        return HttpResponse('oops', status=404)

def async(request, id):
    try:
        task = AsyncTask.objects.get(id=id)
        if task.is_end:
            return HttpResponse(task.result)
        else:
            return HttpResponse('partial:%s' % task.status)
    except ObjectDoesNotExist:
        return HttpResponse('oops', status=404)

"""
установка gearman
sudo apt-get install gearman

установка python-gearman
sudo pip install -e git+https://github.com/Yelp/python-gearman.git@2ed9d88941e31e3358a0b80787254d0c2cfaa78a#egg=gearman-dev

установка python-gearman-commands
sudo pip install django-gearman-commands
sudo pip install prettytable==0.5


прописать в settings.py
INSTALLED_APPS = (
       # ...installed apps...
       'django_gearman_commands',
)
GEARMAN_SERVERS = ['127.0.0.1:4730']


тестовый исполнитель задача(worker) в TZM/async/management/commands/gearman_test.py
запуск ./manage.py gearman_test
для постоянной работы рекомендую сделать это через supervisor
http://pypi.python.org/pypi/django-gearman-commands/0.1
"""
