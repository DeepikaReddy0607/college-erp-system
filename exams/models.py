from django.db import models
from academics.models import CourseOffering

class ExamType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Exam Type"
        verbose_name_plural = "Exam Types"

    def __str__(self):
        return self.name

class Exam(models.Model):
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE
    )

    exam_type = models.ForeignKey(
        ExamType,
        on_delete=models.CASCADE
    )

    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    room = models.CharField(max_length=50, blank=True)

    instructions = models.TextField(blank=True)

    class Meta:
        unique_together = ("offering", "exam_type")
        ordering = ["exam_date", "start_time"]

    def __str__(self):
        return f"{self.offering.course.course_code} - {self.exam_type.name}"

class ExamSyllabus(models.Model):
    exam = models.OneToOneField(
        Exam,
        on_delete=models.CASCADE,
        related_name="syllabus"
    )
    syllabus_text = models.TextField(blank=True)
    syllabus_file = models.FileField(
        upload_to="exam_syllabus/",
        blank=True,
        null=True
    )
