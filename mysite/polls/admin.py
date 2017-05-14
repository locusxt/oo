# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


from .models import MyUser, Course, SignupInfo, Process
# Register your models here.

admin.site.register(MyUser)
admin.site.register(Course)
admin.site.register(SignupInfo)
admin.site.register(Process)