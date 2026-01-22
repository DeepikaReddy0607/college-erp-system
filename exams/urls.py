from django.urls import path
from . import views
urlpatterns = [
    path("student/", views.student_exam_schedule, name="student_exam_schedule"),
    path("student/syllabus/",views.student_exam_syllabus,name="student_exam_syllabus"),
]
