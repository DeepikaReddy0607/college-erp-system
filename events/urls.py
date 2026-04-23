from django.urls import path
from . import views
app_name = "events"
urlpatterns = [

    # Student
    path("student/upcoming/", views.student_upcoming_events, name="student_upcoming_events"),
    path("student/past/", views.student_past_events, name="student_past_events"),
    path("student/my-events/", views.my_events, name="my_events"),
    path("<int:pk>/", views.student_event_detail, name="student_event_detail"),
    path("<int:pk>/register/", views.register_event, name="register_event"),
    path("<int:pk>/cancel/", views.cancel_registration, name="cancel_registration"),

    # Admin
    path("admin/list/", views.admin_event_list, name="admin_event_list"),
]