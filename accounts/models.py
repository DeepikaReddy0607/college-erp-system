from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
        ('ADMIN', 'Admin'),
    )

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['email','role']

class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    section = models.CharField(max_length=1)

    def __str__(self):
        return self.user.username
    
class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)

    is_hod = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.email