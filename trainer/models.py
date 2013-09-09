# -*- coding: utf-8 -*-
from django.db import models
import datetime, sys
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import hashlib


class Photo(models.Model):
    user = models.ForeignKey(auth_models.User)
    img = models.ImageField(upload_to = 'photo')
    def __unicode__(self):
        return 'Photo for ' + self.user.username

TYPE_CATEGORY_CHOICES = (
    (1, u'Модуль'),
    (2, u'Тема'),
    (3, u'Дидактическая единица'),
)
class RECategory(models.Model):
    """
    Модель модулей(тем и дидактических единиц) и связей между ними
    """
    parent = models.ForeignKey('self', verbose_name = u'Раздел верхнего уровня', null=True, blank=True)
    type_category = models.IntegerField(u'Тип', choices=TYPE_CATEGORY_CHOICES)
    number = models.IntegerField(u'Номер')
    name = models.CharField(u'Название', max_length=256)
    is_3d = models.BooleanField(u'3D?', default=False)
    role = models.IntegerField(u'Роль', default=0)
    description = models.TextField(u'Описание', null=True, blank=True)
    codevideo = models.TextField(u'Код')
	
    def json(self):
		return { 'name': self.name, 'description': self.description, 'number': self.number}
		
    class Meta:
        verbose_name = u'Модули, темы, дидактические единицы'
        verbose_name_plural = u'Модули, темы, дидактические единицы'

    def __unicode__(self):
        return u'%s. %s' % (self.number, self.name)

    def children(self):
        return RECategory.objects.filter(parent=self).order_by('number')

    def get_ids(self, ids=None):
        if ids is None:
            ids = [self.id]
        for child in self.children():
            ids.append(child.id)
            child.get_ids(ids)
        return ids

TYPE_LOG_CHOICES = (
    (1, u'Демонстрация'),
    (2, u'Обучение'),
    (3, u'Симуляция'),
    (4, u'Контроль'),
    (5, u'Тестирование'),
)
class RELog(models.Model):
    """
    Модель действий пользователя
    """
    category = models.ForeignKey(RECategory)
    user = models.ForeignKey(auth_models.User)
    type_log = models.IntegerField(u'Тип', choices=TYPE_LOG_CHOICES)
    rating = models.IntegerField(u'Оценка')
    date = models.DateTimeField(u'Начало', auto_now_add=True)
    seconds = models.PositiveIntegerField(u'Длительность', null=True, blank=True)
    context = models.PositiveIntegerField(u'Идентификатор контекста', null=True, blank=True)
    description = models.TextField(u'Пометки', null=True, blank=True)

    class Meta:
        verbose_name = u'Лог'
        verbose_name_plural = u'Логи'

    def __unicode__(self):
        return u'%s' % self.date
        
    def get_model_fields(model):
		return model._meta.fields


class RETestQuestion(models.Model):
    """
    Модель вопросов тестов
    """
    category = models.ForeignKey(RECategory, verbose_name = u'Категория')
    text = models.CharField(u'Текст', max_length=256)
    img = models.ImageField(upload_to = 'test_image/', null=True, blank=True)
    level = models.IntegerField(u'Уровень сложности')
    type = models.BooleanField(u'Вопрос на соответствие', default=False)
	
    class Meta:
        verbose_name = u'Вопрос'
        verbose_name_plural = u'Вопросы'

    def __unicode__(self):
        return u'%s' % self.text


class RETestAnswer(models.Model):
    """
    Модель правильных ответов на вопросы тестов
    """
    question = models.ForeignKey(RETestQuestion)
    name = models.CharField(u'Название', max_length=256)
    is_correct = models.BooleanField(u'Правильный?', default=False)

    class Meta:
        verbose_name = u'Ответ'
        verbose_name_plural = u'Ответы'

    def __unicode__(self):
        return u'%s' % self.name

'''
class RESyncBlock(models.Model):
    """
    Модель блока, содержащего управляющие действия пользователя
    """
    category = models.ForeignKey(RECategory)
    date = models.DateTimeField(u'Начало', auto_now_add=True)
    date_end = models.DateTimeField(u'Окончание', null=True, blank=True)
    type_log = models.IntegerField(u'Тип', choices=TYPE_LOG_CHOICES)

    class Meta:
        verbose_name = u'Блок синхронизации'
        verbose_name_plural = u'Блоки синхронизация'

    def __unicode__(self):
        return u'%s' % self.category


class RESyncLog(models.Model):
    """
    Модель управляющих действий пользователя
    """
    block = models.ForeignKey(RESyncBlock)
    date = models.DateTimeField(u'Начало', auto_now_add=True)
    key = models.CharField(u'Клавиша', max_length=2)

    class Meta:
        verbose_name = u'Лог синхронизации'
        verbose_name_plural = u'Логи синхронизация'

    def __unicode__(self):
        return u'%s' % self.key
'''

class RESyncState(models.Model):
    """
    Модель состояния синхронизации
    """
    is_sync = models.BooleanField(u'Синхронизация', default=False)

    class Meta:
        verbose_name = u'Состояния синхронизации'
        verbose_name_plural = u'Состояния синхронизации'

    def __unicode__(self):
        return u'%s' % self.is_sync

    @staticmethod
    def get_state():
        sync_state = RESyncState.objects.all()
        if not sync_state:
            sync_state = RESyncState.objects.create(is_sync=False)
        else:
            sync_state = sync_state[0]
        return sync_state


class RESync(models.Model):
    """
    Модель управляющих действий пользователя
    """
    user = models.ForeignKey(auth_models.User)
    date = models.DateTimeField(u'Начало', auto_now_add=True)
    key = models.CharField(u'Клавиша', max_length=255)
    context = models.CharField(u'Фильтр', max_length=32, db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = u'Лог синхронизации'
        verbose_name_plural = u'Логи синхронизации'

    def __unicode__(self):
        return u'%s: %s: %s: %s' % (self.user, self.date, self.key, self.context)



"""
class Ochenka(models.Model):
	name_ochenki = models.CharField(u'Название оценки', max_length=1000)
 
class Uchebnaya_Zadacha(models.Model):
	soderzh_dey_oper = models.CharField(u'Содержание действия оператора', max_length=1000)
	nabl_rez_deystvia = models.CharField(u'Наблюдаемые результаты действия', max_length=1000)
	upragnenie = models.ForeignKey(RETest)

class Otsenka_po_kvu_oshibok(models.Model):
	min_errors = models.IntegerField(u'Минимальное количество ошибок')
	max_errors = models.IntegerField(u'Максимальное количество ошибок')
	uchebnaya_zadacha = models.ForeignKey(Uchebnaya_Zadacha)
	ochenka = models.ForeignKey(Ochenka)

class Urov_slogh(models.Model):
	name_urov_sl = models.CharField(u'Название уровня сложности', max_length=1000)
	kol_ball = models.IntegerField(u'Количество баллов', max_length=1000)
	time_vipoln_zad = models.CharField(u'Время выполнения задания', max_length=1000)
	rel_to_test = models.ManyToManyField(RETest)
	
class Vozm_ochibka(models.Model):
	opis_och = models.CharField(u'Описание ошибки', max_length=1000)
	shtr_ball = models.IntegerField(u'Штрафной балл', max_length=1000)
	text_soobch = models.CharField(u'Текстовое сообщение', max_length=1000)
	nal_zv_sign = models.CharField(u'Наличие звукового сигнала', max_length=1000)
	uchebnaya_zadacha = models.ForeignKey(Uchebnaya_Zadacha) 


class Vipoln_uch_zad(models.Model):
	vremya_vypoln = models.CharField(u'Время выполнения', max_length=1000)
	vipoln_uprag = models.ForeignKey(RETest)
	uchebnaya_zadacha= models.ForeignKey(Uchebnaya_Zadacha)

 
class Ochibka_vipoln_zad(models.Model):
	vipoln_uch_zad = models.ForeignKey(Vipoln_uch_zad)
	vozm_ochibka= models.ForeignKey(Vozm_ochibka)

class Otcenka_po_vrem_vip(models.Model):
	min_time = models.CharField(u'Минимальное время', max_length=1000)
	max_time = models.CharField(u'Максимальное время', max_length=1000)
	uchebnaya_zadacha = models.ForeignKey(Uchebnaya_Zadacha)
	ochenka = models.ForeignKey(Ochenka)
"""
