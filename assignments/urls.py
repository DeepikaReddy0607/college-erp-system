from django.urls import path
from . import views

urlpatterns = [

    # FACULTY ASSIGNMENT MANAGEMENT
    path(
        "faculty/assignments/",
        views.faculty_assignments,
        name="faculty_assignments"
    ),

    path(
        "faculty/assignments/create/",
        views.create_assignment,
        name="create_assignment"
    ),

    path(
        "faculty/assignments/<int:assignment_id>/edit/",
        views.edit_assignment,
        name="edit_assignment"
    ),

    path(
        "faculty/assignments/<int:assignment_id>/close/",
        views.close_assignment,
        name="close_assignment"
    ),

    path(
        "faculty/assignments/<int:assignment_id>/delete/",
        views.delete_assignment,
        name="delete_assignment"
    ),

    # SUBMISSIONS
    path(
        "faculty/assignments/<int:assignment_id>/submissions/",
        views.assignment_submissions,
        name="assignment_submissions"
    ),

    path(
        "faculty/assignments/<int:assignment_id>/download/",
        views.download_all_submissions,
        name="download_all_submissions"
    ),

    path(
        "faculty/submission/<int:submission_id>/grade/",
        views.grade_submission,
        name="grade_submission"
    ),

    # STUDENT ASSIGNMENTS
    path(
        "student/assignments/",
        views.student_assignments,
        name="student_assignments"
    ),

    path(
        "student/assignments/<int:assignment_id>/submit/",
        views.submit_assignment,
        name="submit_assignment"
    ),

]