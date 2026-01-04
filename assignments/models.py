from django.db import models
from accounts.models import FacultyProfile, StudentProfile
from academics.models import Course

class Assignment(models.Model):
    subject = models.ForeignKey(Course, on_delete = models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    due_date = models.DateTimeField()
    attachment = models.FileField(
        upload_to="assignments/resources",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject.code} - {self.title}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    file = models.FileField(upload_to="assignments/submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.roll_no} - {self.assignment.title}"
