from django.db import models
from accounts.models import StudentProfile
from academics.models import CourseOffering

class Assignment(models.Model):
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    due_date = models.DateTimeField()
    attachment = models.FileField(
        upload_to="assignments/resources",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.offering.course.code} - {self.title}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name="assignment_submissions"
    )
    file = models.FileField(upload_to="assignments/submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    graded_at = models.DateTimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    class Meta:
        unique_together = ("assignment", "student")

    def save(self, *args, **kwargs):
        if self.submitted_at and self.submitted_at > self.assignment.due_date:
            self.is_late = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.roll_no} - {self.assignment.title}"
