from django.contrib import admin
from .models import (
    Department,
    StudentProfile,
    FacultyProfile,
    OTPVerification,
)

admin.site.register(Department)
admin.site.register(StudentProfile)
admin.site.register(FacultyProfile)
admin.site.register(OTPVerification)
from django.contrib.auth import get_user_model
User = get_user_model()

admin.site.register(User)
