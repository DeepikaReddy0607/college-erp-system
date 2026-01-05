from django.urls import path
from .views import student_notifications
from . import views
urlpatterns = [
    path("student/", student_notifications, name="student_notifications"),
    path("read/<int:pk>/",views.mark_notification_read,name="mark_notification_read"),
    path("ajax/read/<int:pk>/",views.ajax_mark_notification_read,name="ajax_mark_notification_read"),
    path("faculty/send/",views.faculty_send_notification,name="faculty_send_notification"),
    path("faculty/",views.faculty_notifications,name="faculty_notifications"),
]   
