from django.urls import path
from grades import views
from .views import download_marks, exam_dashboard
urlpatterns = [
    path("dashboard/", exam_dashboard, name="exam_dashboard"),
    path(
        "upload-grades/<int:offering_id>/",
        views.exam_upload_final_grades,
        name="exam_upload_final_grades"
    ),

    # Upload SGPA / CGPA
    path(
        "upload-semester-results/<int:semester_id>/",
        views.exam_upload_semester_results,
        name="exam_upload_semester_results"
    ),

    # Freeze results
    path(
        "freeze-results/<int:offering_id>/",
        views.exam_freeze_results,
        name="exam_freeze_results"
    ),
    path("download-marks/<int:offering_id>/", download_marks, name="download_marks"),
    path("year/<int:year>/", views.year_semester_view, name="year_semester_view"),
]