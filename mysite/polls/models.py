# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class MyUser(models.Model):
	name = models.CharField(max_length=17)
	mytype = models.CharField(max_length=17)
	school = models.CharField(max_length=17)
	credit_current = models.IntegerField(default=0)
	credit_limit = models.IntegerField(default=0)
	def addCurrent(self, num=1):
		self.credit_current += num
		self.save()
	def subCurrent(self, num=1):
		self.credit_current -= num
		self.save()

class Course(models.Model):
	teacher = models.ForeignKey(MyUser)
	name = models.CharField(max_length=17)
	current = models.IntegerField(default=0)
	limit = models.IntegerField(default=70)
	credit = models.IntegerField(default=2)
	time = models.CharField(max_length=17)
	place = models.CharField(max_length=17)
	description = models.CharField(max_length=17)
	syllabus = models.CharField(max_length=77, default='')
	standard = models.CharField(max_length=77, default='')
	mytype = models.CharField(max_length=7, default='必修')
	def isFull(self):
		return self.current >= self.limit
	def addCurrent(self, num=1):
		self.current += num
		self.save()
	def subCurrent(self, num=1):
		self.current -= num
		self.save()

class SignupInfo(models.Model):
	student = models.ForeignKey(MyUser)
	course = models.ForeignKey(Course)
	state = models.CharField(max_length=17)
	gpa = models.FloatField(default=4.0)

class Process(models.Model):
	startTime = models.DateTimeField('start')
	endTime = models.DateTimeField('end')
	mytype = models.CharField(max_length=17)
	state = models.CharField(max_length=17)


