from django.urls import path
from . import views
from .views import otp_verify_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home_view, name = "home"),
    path('login/', views.login_view, name = 'login'),
    path('register/', views.register_view, name = 'register'),
    path('otp/',views.otp_view, name = 'otp'),
    path('otp/verify/', otp_verify_view, name = "otp_verify"),
    path('set-password/', views.set_password_view, name = 'password'),
    path('dashboard/', views.dashboard_view, name = 'dashboard'),
    path("faculty/dashboard/", views.faculty_dashboard_view, name="faculty_dashboard"),
    path("faculty/courses/", views.faculty_courses_view, name="faculty_courses"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),

]