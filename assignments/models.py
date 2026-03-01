from django.db import models
from accounts.models import StudentProfile
from academics.models import CourseOffering

class Assignment(models.Model):
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
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
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE,related_name="assignment_submissions")
    file = models.FileField(upload_to="assignments/submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.roll_no} - {self.assignment.title}"
