from django.db import models
from django.conf import settings
from academics.models import Course, CourseOffering

User = settings.AUTH_USER_MODEL


class Doubt(models.Model):
    DOUBT_TYPE_CHOICES = [
        ("SECTION", "Section Doubt"),
        ("FACULTY", "Faculty Doubt"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="asked_doubts"
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    doubt_type = models.CharField(
        max_length=10,
        choices=DOUBT_TYPE_CHOICES
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DoubtAnswer(models.Model):
    doubt = models.ForeignKey(
        Doubt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    is_accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

