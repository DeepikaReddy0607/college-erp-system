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
    path(
        "download-template/<int:offering_id>/",
        views.download_grades_template,
        name="download_grades_template"
    ),
    path(
    "download-final-template/<int:offering_id>/",
    views.download_final_grades_template,
    name="download_final_grades_template"
    ),
    path(
    "exam/offering/<int:offering_id>/release/",
    views.exam_release_results,
    name="exam_release_results"
    ),
    path(
    "release-semester/<int:semester_id>/",
    views.exam_release_semester_results,
    name="exam_release_semester_results"
),
]