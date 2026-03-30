from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from academics.models import Course

User = get_user_model()


class MarksSubmission(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="marks_submissions"
    )

    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE,
        related_name="marks_submissions"
    )

    minor1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minor2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mid = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="marks_entered_by"
    )

    submitted_at = models.DateTimeField(auto_now=True)

    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "course_offering")
        indexes = [
            models.Index(fields=["course_offering"]),
            models.Index(fields=["student"])
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            old = MarksSubmission.objects.get(pk=self.pk)
            if old.is_locked:
                raise ValidationError("Locked marks cannot be modified.")
        super().save(*args, **kwargs)

    def lock(self):
        self.is_locked = True
        self.save()

class FinalGrade(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="final_grades"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE,
        related_name="final_grades"
    )

    grade_letter = models.CharField(max_length=2)
    attempt_number = models.IntegerField(default=1)
    is_backlog = models.BooleanField(default=False)
    published_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="grades_published"
    )

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now_add=True)

    is_frozen = models.BooleanField(default=False)

    class Meta:
        unique_together = ["student", "course", "attempt_number"]

    def save(self, *args, **kwargs):
        if self.pk:
            old = FinalGrade.objects.get(pk=self.pk)
            if old.is_frozen:
                raise ValidationError("Frozen grades cannot be modified.")
        super().save(*args, **kwargs)

    def freeze(self):
        self.is_frozen = True
        self.save()

class SemesterResult(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="semester_results"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.CASCADE,
        related_name="semester_results"
    )

    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    published_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="semester_results_published"
    )

    published_at = models.DateTimeField(auto_now_add=True)

    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "semester")

    def save(self, *args, **kwargs):
        if self.pk:
            old = SemesterResult.objects.get(pk=self.pk)
            if old.is_locked:
                raise ValidationError("Locked semester result cannot be modified.")
        super().save(*args, **kwargs)

    def lock(self):
        self.is_locked = True
        self.save()