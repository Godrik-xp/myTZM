from django.db import models
from django.contrib import admin

# Create your models here.



CATHEGORY_CHOICES = ( ('Op.1', 'operator1'), ('Op.2', 'operator2') )

class Session(models.Model):
	time_first = models.DataField() //начало сессии
	time_last = models.DataField() //конец сессии
	teacher = models.CharField(max_length = 30, choices = TEACHER_CHOICES)
	def unicod(self):
		return self.time_first + " " + self.time_last + " " + teacher

TEACHER_CHOICES = (........)

class ObjectDump(models.Model):
	objectname = models.CharField(max_length=20, choices = OBJECT_CHOICES)
	x = models.FloatField(...max_digits = 5, decimal_places = 3)
	y = models.FloatField(...max_digits = 5, decimal_places = 3)
	z = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_xx = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_xy = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_xz = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_yx = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_yy = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_yz = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_zx = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_zy = models.FloatField(...max_digits = 5, decimal_places = 3)
	rot_zz = models.FloatField(...max_digits = 5, decimal_places = 3)
	time = models.TimeField()

OBJECT_CHOICES = (........)


class Key(models.Model):
	name_key = models.CharField(max_length=10, choices = KEY_CHOICES) //какая клавиша
	time_key = models.TimeField() //время налаживания
	role = models.CharField(max_length = 10, choices = ROLE_CHOICES)
	number_session = models.IntegerField() //номер сессии
	
KEY_CHOICES = (........)

SCENARIO_CHOICES = (........)

ROLE_CHOICES = (........)

MODE_CHOICES = (........)

class Task(models.Model):
	number = models.IntegerField()
	scenario = models.CharField(max_length=50, choices = SCENARIO_CHOICES)
	role = models.CharField(max_length=10, choices = CATHEGORY_CHOICES)
	text_task = models.TextField()

