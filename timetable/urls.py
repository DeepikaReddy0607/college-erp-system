from django.urls import path
from .views import student_timetable
from . import views

urlpatterns = [
    path("student/", student_timetable, name="student_timetable"),
    path("faculty/", views.faculty_timetable, name="faculty_timetable"),
]
