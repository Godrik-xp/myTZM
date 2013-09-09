# -*- coding: utf-8 -*-
import time

import django_gearman_commands
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson

from TZM.async.models import *

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
   @property
   def task_name(self):
       return 'test'

   def do_job(self, job_data):
        try:
            task = AsyncTask.objects.get(id=job_data)
        except ObjectDoesNotExist:
            pass
        else:
            task.status = 0
            for i in range(10): 
                time.sleep(2)
                task.status += 10
                task.save()
            try:
                data = simplejson.loads(task.data)
                result = data + 1
                task.result = simplejson.dumps(result)
            except:
                pass
            else:
                task.is_end= True
                task.save()
