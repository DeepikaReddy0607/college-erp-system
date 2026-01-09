from django.urls import path
from grades import views

urlpatterns = [
    path("student/", views.student_grades, name="student_grades"),
    path("upload/<int:subject_id>/", views.upload_grades, name="upload_grades"),
]
