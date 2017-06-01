#! usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, get_object_or_404 
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages  
import time
import datetime
import random

from django import forms
from models import MyUser, Course, SignupInfo, Process
from django.contrib.admin import widgets
from django.forms.extras.widgets import SelectDateWidget

class Teacher:
    def __init__(self, user):
        self.teacher = user
    def addCourse(self, info):
        Course.objects.create(teacher=self.teacher, 
            name = info['coursename'],
            limit = info['limit'],
            time = info['time'],
            place = info['place'],
            description = info['desc'],
            credit = info['credit'],
            syllabus = info['syllabus'],
            standard = info['standard'],
            mytype = info['mytype']
            )
    def getCourses(self):
        courses = Course.objects.filter(teacher=self.teacher)
        return courses
    def getCourseInfo(self, courseid):#have not tested
        targetcourse = get_object_or_404(Course, id=courseid)
        signupinfo = SignupInfo.objects.filter(course = targetcourse)
        return {'course':targetcourse, 'sinfo':signupinfo}
    def delStudent(self, courseid, studentid):
        targetcourse = get_object_or_404(Course, id=courseid)
        targetstudent = get_object_or_404(MyUser, id=studentid)
        a = SignupInfo.objects.filter(course = targetcourse, student = targetstudent)
        targetcourse.subCurrent(len(a))
        a.delete()


class Student:
    def __init__(self, user):
        self.student = user
        self.ps = ProcessState()
    def signup(self, courseid):
        pinfo = self.ps.getinfo()
        if (not pinfo['pre']) and (not pinfo['signup']):
            return "非预选或者补选时间"
        targetcourse = get_object_or_404(Course, id=courseid)
        sinfo = SignupInfo.objects.filter(course = targetcourse, student = self.student)
        if len(sinfo) > 0:
            return "已经选课"
        if self.student.credit_current + targetcourse.credit > self.student.credit_limit:
            return "选课超出学分上限"
        if targetcourse.current + 1 > targetcourse.limit and (not pinfo['pre']):
            return "非预选时间，选课人数不可超过上限"
        SignupInfo.objects.create(
                student = self.student,
                course = targetcourse,
                state = "default"
            )
        targetcourse.addCurrent()
        self.student.addCurrent(targetcourse.credit)
        return "success"
    def getAllCourses(self):
        courses = Course.objects.all()
        signupinfo = SignupInfo.objects.filter(student = self.student)
        signedid= []
        for s in signupinfo:
            signedid.append(s.course.id)
        courses = courses.exclude(id__in = signedid)
        return courses
    def getSignupInfo(self):
        signupinfo = SignupInfo.objects.filter(student = self.student)
        return signupinfo
    def cancelSignup(self, courseid):
        pinfo = self.ps.getinfo()
        if (not pinfo['cancel']):
            return "非退选时间"
        targetcourse = get_object_or_404(Course, id=courseid)
        a = SignupInfo.objects.filter(course = targetcourse, student = self.student)
        targetcourse.subCurrent(len(a))
        self.student.subCurrent(targetcourse.credit)
        a.delete()
        return "success"

class MyAdmin:
    def __init__(self, user):
        self.student = user
    def addProcess(self, info):
        Process.objects.create(startTime = info['startTime'], endTime = info['endTime'], mytype = info['mytype'], state = 'default')
    def getAllProcesses(self):
        processes = Process.objects.all()
        return processes
    def deleteProcess(self, processid):
        Process.objects.filter(id = processid).delete()
    def draw(self):
        courses = Course.objects.all()
        for c in courses:
            current = c.current
            limit = c.limit
            infos = SignupInfo.objects.filter(course = c)
            if current > limit:
                rm_num = current - limit
                rm_list = random.sample(infos, rm_num)
                c.subCurrent(rm_num)
                for r in rm_list:
                    r.student.subCurrent(r.course.credit)
                    SignupInfo.objects.filter(id = r.id).delete()


class ProcessState:
    def __init__(self):
        self.statelist = []
    def getStateList(self):
        pl = Process.objects.filter(startTime__lte=datetime.date.today()).filter(endTime__gte=datetime.date.today())
        for p in pl:
            self.statelist.append(p.mytype)
        self.statelist = list(set(self.statelist))
        return self.statelist
    def getMsg(self):
        sl = self.getStateList()
        mystr = "当前可进行："
        for s in sl:
            mystr += s + ' '
        return mystr
    def getinfo(self):
        res = {'pre':False, 'signup':False, 'cancel':False}
        sl = self.getStateList()
        for s in sl:
            if s == "预选":
                res['pre'] = True
            elif s == "补选":
                res['signup'] = True
            elif s == "退选":
                res['cancel'] = True
        return res

# Create your views here.

##basic login logout view
def index(req):
    username = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = username)
    # myadmin = MyAdmin(user)
    # myadmin.draw()
    now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))  
    ip= ""
    if req.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ip =  req.META['HTTP_X_FORWARDED_FOR']  
    else:  
        ip = req.META['REMOTE_ADDR']  
    if username == '':
        response = HttpResponseRedirect('/polls/login')
        return response
    return render(req, 'index.html', {'user':username, 'time':now, 'ip':ip})
    # return HttpResponse("Hello, world. You're at the polls index." + username)

class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=17)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

def login(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            user = MyUser.objects.filter(name = username)
            if user:
                response = HttpResponseRedirect('/polls/index')
                response.set_cookie('username',username,3600)
                return response
            else:
                messages.add_message(req,messages.ERROR,'账号或密码错误') 
                return HttpResponseRedirect('/polls/login')
    else:
        uf = UserForm()
    return render(req, 'login.html', {'uf':uf})

def logout(req):
    response = HttpResponseRedirect('/polls/login')
    response.delete_cookie('username')
    messages.add_message(req,messages.INFO,'已注销') 
    return response




##Teacher view
COURSE_CHOICES = (
    ('必修', '必修'),
    ('选修', '选修'),
    )

class NewCourseForm(forms.Form):
    coursename = forms.CharField(label='课程名', max_length=17)
    limit = forms.IntegerField(label='人数上限')
    credit = forms.IntegerField(label='学分')
    mytype = forms.ChoiceField(choices=COURSE_CHOICES,label='类型')
    time = forms.CharField(label='上课时间', max_length=17)
    place = forms.CharField(label='上课地点', max_length=17)
    desc = forms.CharField(label='课程描述', max_length=17)
    syllabus = forms.CharField(label='教学大纲', max_length=77)
    standard = forms.CharField(label='评分标准', max_length=77)

def addNewCourse(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    teacher = Teacher(user)
    # teacher.getCourses()
    if req.method == 'POST':
        ncf = NewCourseForm(req.POST)
        if ncf.is_valid():
            res = {}
            res['coursename'] = ncf.cleaned_data['coursename']
            res['limit'] = ncf.cleaned_data['limit']
            res['time'] = ncf.cleaned_data['time']
            res['place'] = ncf.cleaned_data['place']
            res['desc'] = ncf.cleaned_data['desc']
            res['credit'] = ncf.cleaned_data['credit']
            res['syllabus'] = ncf.cleaned_data['syllabus']
            res['standard'] = ncf.cleaned_data['standard']
            res['mytype'] = ncf.cleaned_data['mytype']
            teacher.addCourse(res)
            response = HttpResponseRedirect('/polls/addcourse')
            messages.add_message(req, messages.INFO, res['coursename'] + '添加成功') 
            return response
    else:
        ncf = NewCourseForm()
    return render(req, 'addcourse.html', {'ncf':ncf, 'user':uname})

def getCourses(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    teacher = Teacher(user)
    courses = teacher.getCourses()
    return render(req, 'getcourses.html', {'user':uname, 'courses':courses})

def manageCourse(req, courseid):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    teacher = Teacher(user)
    courseinfo = teacher.getCourseInfo(courseid)
    return render(req, 'managecourse.html', {'user':uname, 'course':courseinfo['course'], 'sinfo':courseinfo['sinfo']})

def delStudent(req, courseid, studentid):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    teacher = Teacher(user)
    teacher.delStudent(courseid, studentid)
    return manageCourse(req, courseid)




##Student view
def getAllCourses(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    student = Student(user)
    courses = student.getAllCourses()
    ps = ProcessState()
    messages.add_message(req, messages.INFO, ps.getMsg())
    select_credit = 0
    must_credit = 0
    for s in courses:
        if s.mytype == "必修":
            must_credit += s.credit
        else:
            select_credit += s.credit
    return render(req, 'getallcourses.html', {'user':uname, 'courses':courses, 'u':user, 'must':must_credit, 'select':select_credit})

def signup(req, courseid):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    student = Student(user)
    res = student.signup(courseid)
    if res == "success":
        messages.add_message(req, messages.INFO, "选课成功")
    else:
        messages.add_message(req, messages.ERROR, res)
    user = get_object_or_404(MyUser, name = uname)
    student = Student(user)
    return getAllCourses(req)

def getSignupInfo(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    student = Student(user)
    res = student.getSignupInfo()
    select_credit = 0
    must_credit = 0
    for s in res:
        if s.course.mytype == "必修":
            must_credit += s.course.credit
        else:
            select_credit += s.course.credit
    return render(req, 'getsignupinfo.html', {'user':uname,'u':user, 'sinfo':res, 'must':must_credit, 'select':select_credit})

def cancelSignup(req, courseid):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    student = Student(user)
    res = student.cancelSignup(courseid)
    messages.add_message(req, messages.WARNING, res) 
    return getSignupInfo(req)

##MyAdmin view
PROCESS_CHOICES = (
    ('预选', '预选'),
    ('补选', '补选'),
    ('退选', '退选'),
    )

class NewProcessForm(forms.Form):
    startTime = forms.DateTimeField(widget=SelectDateWidget(), label = '开始时间')
    endTime = forms.DateTimeField(widget=SelectDateWidget(), label = '结束时间')
    mytype = forms.ChoiceField(choices=PROCESS_CHOICES,label='流程类型')

def addProcess(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    myadmin = MyAdmin(user)
    if req.method == 'POST':
        npf = NewProcessForm(req.POST)
        if npf.is_valid():
            res = {}
            res = npf.cleaned_data
            myadmin.addProcess(res)
            response = HttpResponseRedirect('/polls/addprocess')
            messages.add_message(req, messages.INFO, res['mytype'] + '添加成功') 
            return response
    else:
        ncf = NewProcessForm()
    return render(req, 'addprocess.html', {'npf':ncf, 'user':uname})

def getAllProcesses(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    myadmin = MyAdmin(user)
    processes = myadmin.getAllProcesses()
    return render(req, 'getallprocesses.html', {'user':uname, 'processes':processes, 'u':user})

def deleteProcess(req, processid):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    myadmin = MyAdmin(user)
    myadmin.deleteProcess(processid)
    return getAllProcesses(req)

def draw(req):
    uname = req.COOKIES.get('username','')
    user = get_object_or_404(MyUser, name = uname)
    myadmin = MyAdmin(user)
    myadmin.draw()
    messages.add_message(req, messages.INFO, '抽签已经完成') 
    return index(req)