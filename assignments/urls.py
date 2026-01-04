from django.urls import path
from assignments.views import create_assignment, faculty_assignments, assignment_submissions
from . import views
urlpatterns = [
    path("faculty/assignments/", faculty_assignments, name = "faculty_assignments"),
    path("faculty/assignments/create/",create_assignment,name = "create_assignment"),
    path("faculty/assignmets/<int:assignment_id>/submissions",assignment_submissions, name = "assignment_submissions"),
    path("student/assignments/", views.student_assignments, name = "student_assignments"),
    path("student/assignments/<int:assignment_id>/submit/", views.submit_assignment,name="student_assignment_submit"),
]