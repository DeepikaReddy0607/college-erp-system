from django.urls import path
from . import views

app_name = "grades"

urlpatterns = [

    # =========================
    # FACULTY
    # =========================
    path(
        "faculty/offering/<int:offering_id>/submit/",
        views.faculty_submit_marks,
        name="faculty_submit_marks"
    ),

    # =========================
    # EXAM SECTION
    # =========================
    path(
        "exam/offering/<int:offering_id>/upload-final/",
        views.exam_upload_final_grades,
        name="exam_upload_final_grades"
    ),

    path(
        "exam/semester/<int:semester_id>/upload-results/",
        views.exam_upload_semester_results,
        name="exam_upload_semester_results"
    ),

    path(
        "exam/offering/<int:offering_id>/freeze/",
        views.exam_freeze_results,
        name="exam_freeze_results"
    ),

    # =========================
    # STUDENT
    # =========================
    path(
        "student/my-grades/",
        views.student_view_grades,
        name="student_view_grades"
    ),
]