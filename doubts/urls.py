from django.urls import path
from . import views

urlpatterns = [

    # Student views
    path("student/", views.student_doubts, name="student_doubts"),
    path("student/ask/", views.ask_doubt, name="ask_doubt"),

    # Doubt thread (shared)
    path("doubt/<int:doubt_id>/", views.doubt_detail, name="doubt_detail"),

    # Faculty dashboard
    path("faculty/", views.faculty_doubts, name="faculty_doubts"),

    # Answer actions
    path("answers/<int:answer_id>/upvote/", views.toggle_upvote, name="toggle_upvote"),
    path("answers/<int:answer_id>/accept/", views.accept_answer, name="accept_answer"),
]