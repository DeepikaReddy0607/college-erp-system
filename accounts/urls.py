from django.urls import path
from . import views
from .views import otp_verify_view

urlpatterns = [
    path('',views.home_view, name = "home"),
    path('login/', views.login_view, name = 'login'),
    path('register/', views.register_view, name = 'register'),
    path('otp/',views.otp_view, name = 'otp'),
    path('otp/verify/', otp_verify_view, name = "otp_verify"),
    path('set-password/', views.set_password_view, name = 'password'),
    path('dashboard/', views.dashboard_view, name = 'dashboard'),
]