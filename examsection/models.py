from django.db import models

from attendance.models import User

class ExamProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)