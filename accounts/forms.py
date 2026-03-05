from django import forms
from .models import StudentProfile, User


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class StudentProfileImageForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']