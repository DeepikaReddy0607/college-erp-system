from django.urls import path
from . import views

urlpatterns = [
    path("faculty/",views.faculty_attendance_landing,name="faculty_attendance"),
    path("faculty/mark/<int:offering_id>/", views.mark_attendance,name="faculty_attendance_mark"),
    path("faculty/history/<int:offering_id>/",views.attendance_history,name="attendance_history"),
    path("faculty/edit/<int:session_id>/",views.edit_attendance,name="attendance_edit"),
    path("student/", views.student_attendance_view, name="student_attendance"),
    path("faculty/<int:offering_id>/export/",views.export_attendance_csv,name="export_attendance_csv"),
]
