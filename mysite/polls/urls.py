from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^addcourse$', views.addNewCourse, name='add course'),
    url(r'^getcourses$', views.getCourses, name='get courses'),
    url(r'^(?P<courseid>[0-9]+)/manage/$', views.manageCourse, name='manage'),
    url(r'^(?P<courseid>[0-9]+)/delete/(?P<studentid>[0-9]+)$', views.delStudent, name='delete student'),
    url(r'^signup$', views.getAllCourses, name='get all courses'),
    url(r'^(?P<courseid>[0-9]+)/signup/$', views.signup, name='signup'),
    url(r'^lookup$', views.getSignupInfo, name='get signup info'),
    url(r'^(?P<courseid>[0-9]+)/cancel/$', views.cancelSignup, name='cancel signup'),
    url(r'^addprocess$', views.addProcess, name='add process'),
    url(r'^processmanage$', views.getAllProcesses, name='get all processes'),
    url(r'^deleteprocess/(?P<processid>[0-9]+)$', views.deleteProcess, name='delete process'),
]


