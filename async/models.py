# -*- coding: utf-8 -*-
from django.db import models


class AsyncTask(models.Model):
    """
    Модель асинхронной задачи
    """
    data = models.TextField(u'Данные', null=True, blank=True)
    status = models.IntegerField(u'Процент', default=0)
    is_end = models.BooleanField(u'Выполнена?', default=False)
    result = models.TextField(u'Результат', null=True, blank=True)

    class Meta:
        verbose_name = u'Задача'
        verbose_name_plural = u'Задачи'

    def __unicode__(self):
        return u'%s: %s' % (self.id, self.is_end)