from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================
# GRADE SYSTEM
# ============================
GRADE_POINTS = {
    "Ex": 10,
    "A": 9,
    "B": 8,
    "C": 7,
    "D": 6,
    "P": 5,
    "M": 4,
    "F": 0,
    "X": 0,
}

GRADE_CHOICES = [(k, k) for k in GRADE_POINTS.keys()]

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

    minor1 = models.DecimalField(max_digits=5, decimal_places=2)
    minor2 = models.DecimalField(max_digits=5, decimal_places=2)
    mid = models.DecimalField(max_digits=5, decimal_places=2)
    end = models.DecimalField(max_digits=5, decimal_places=2)

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="marks_submitted_by_faculty"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "course_offering")

    def submit(self):
        if self.is_locked:
            raise ValidationError("Marks already submitted and locked.")
        self.is_locked = True
        self.save()

    def save(self, *args, **kwargs):
        if self.pk:
            old = MarksSubmission.objects.get(pk=self.pk)
            if old.is_locked:
                raise ValidationError("Locked marks cannot be modified.")
        super().save(*args, **kwargs)

class GradeComputation(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grade_computations"
    )
    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE
    )

    computed_grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    computed_by_exam_section = models.BooleanField(default=True)
    computed_at = models.DateTimeField()
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ("student", "course_offering")

    @property
    def grade_point(self):
        return GRADE_POINTS[self.computed_grade]

    def clean(self):
        if not MarksSubmission.objects.filter(
            student=self.student,
            course_offering=self.course_offering,
            is_locked=True
        ).exists():
            raise ValidationError("Marks must be submitted before grade computation.")

class GradeApproval(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grade_approvals"
    )
    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="grades_approved"
    )
    approved_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ("student", "course_offering")

    def approve(self):
        self.is_approved = True
        self.save()

    def clean(self):
        if not GradeComputation.objects.filter(
            student=self.student,
            course_offering=self.course_offering
        ).exists():
            raise ValidationError("Grade must be computed before approval.")

class FinalGrade(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="final_grades"
    )
    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE
    )

    final_grade = models.CharField(max_length=2, choices=GRADE_CHOICES)

    published_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="grades_published"
    )
    published_at = models.DateTimeField(auto_now_add=True)

    is_frozen = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "course_offering")

    @property
    def grade_point(self):
        return GRADE_POINTS[self.final_grade]

    def clean(self):
        if not GradeApproval.objects.filter(
            student=self.student,
            course_offering=self.course_offering,
            is_approved=True
        ).exists():
            raise ValidationError("Grade must be approved before publishing.")

    def save(self, *args, **kwargs):
        if self.pk:
            old = FinalGrade.objects.get(pk=self.pk)
            if old.is_frozen:
                raise ValidationError("Frozen grades cannot be modified.")
        super().save(*args, **kwargs)

    def freeze(self):
        self.is_frozen = True
        self.save()

class GradeAuditLog(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grade_audit_logs"
    )
    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE
    )

    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="grade_actions"
    )
    performed_at = models.DateTimeField(auto_now_add=True)

    previous_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    class Meta:
        ordering = ["-performed_at"]

class MarksEntryWindow(models.Model):
    PHASE_CHOICES = [
        ("minor1", "Minor 1"),
        ("minor2", "Minor 2"),
        ("mid", "Mid"),
        ("end", "End"),
    ]

    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE,
        related_name="marks_windows"
    )

    phase = models.CharField(
        max_length=10,
        choices=PHASE_CHOICES
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ("course_offering", "phase")

    def is_open(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time
