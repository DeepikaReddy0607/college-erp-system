from django.urls import path
from . import views

urlpatterns = [

    path("student/", views.student_doubts, name="student_doubts"),
    path("student/ask/", views.ask_doubt, name="ask_doubt"),
    path("student/<int:doubt_id>/", views.doubt_detail, name="doubt_detail"),

    path("faculty/", views.faculty_doubts, name="faculty_doubts"),
    path("faculty/<int:doubt_id>/", views.doubt_detail, name="faculty_doubt_detail"),
]
