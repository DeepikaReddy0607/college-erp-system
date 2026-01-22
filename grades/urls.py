from django.urls import path
from grades import views

urlpatterns = [
    path("faculty/offering/<int:offering_id>/marks/",views.faculty_submit_marks,name="faculty_submit_marks"),
    path("hod/offering/<int:offering_id>/review-grades/",views.hod_review_computed_grades,name="hod_review_grades"),
    path("hod/offering/<int:offering_id>/publish-grades/",views.hod_publish_and_freeze_grades,name="hod_publish_grades"),
    path("student/grades/",views.student_view_grades,name="student_view_grades"),
]
