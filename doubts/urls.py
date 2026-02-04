from django.urls import path
from . import views

urlpatterns = [

    path("student/", views.student_doubts, name="student_doubts"),
    path("student/ask/", views.ask_doubt, name="ask_doubt"),
    path("student/<int:doubt_id>/", views.doubt_detail, name="student_doubt_detail"),
    path("answers/<int:answer_id>/upvote/",views.toggle_upvote,name="toggle_upvote"),
    path("faculty/", views.faculty_doubts, name="faculty_doubts"),
    path("faculty/<int:doubt_id>/", views.doubt_detail, name="faculty_doubt_detail"),
    path("answers/<int:answer_id>/accept/",views.accept_answer,name="accept_answer"),
]
