from django.urls import path
from events import views

urlpatterns = [
    path('student/upcoming/',views.student_upcoming_events,name='student_upcoming_events'),
    path('student/past/',views.student_past_events,name='student_past_events'),
    path('<int:event_id>/',views.student_event_detail,name='student_event_detail'),
    path('faculty/',views.faculty_events,name='faculty_events'),
    path('admin/list/',views.admin_event_list,name='admin_event_list'),
    path('admin/create/',views.admin_create_event,name='admin_create_event'),
    path('admin/<int:event_id>/disable/',views.admin_disable_event,name='admin_disable_event'),
]
