from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Course(models.Model):
    CATEGORY_CHOICES = [
        ("BSC", "Basic Science Course"),
        ("ESC", "Engineering Science Course"),
        ("PCC", "Program Core Course"),
        ("DEC", "Department Elective"),
        ("OEC", "Open Elective"),
        ("HSC", "Humanities & Social Science"),
    ]

    course_code = models.CharField(max_length=10)
    course_title = models.CharField(max_length=200)

    lecture_hours = models.PositiveSmallIntegerField(default=0)
    tutorial_hours = models.PositiveSmallIntegerField(default=0)
    practical_hours = models.PositiveSmallIntegerField(default=0)

    credits = models.PositiveSmallIntegerField()
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES)

    is_lab = models.BooleanField(default=False)
    is_elective = models.BooleanField(default=False)

    department = models.ForeignKey(
        "accounts.Department",
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("course_code", "department")

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"

class AcademicYear(models.Model):
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ("start_year", "end_year")

    def save(self, *args, **kwargs):
        if self.is_active:
            AcademicYear.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_year}-{str(self.end_year)[-2:]}"

class Semester(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE
    )
    year = models.PositiveSmallIntegerField()      
    semester = models.PositiveSmallIntegerField()  

    class Meta:
        unique_together = ("academic_year", "year", "semester")

    def clean(self):
        if self.semester not in [1, 2]:
            raise ValidationError("Semester must be 1 or 2")
        if self.year not in [1, 2, 3, 4]:
            raise ValidationError("Year must be between 1 and 4")

    def __str__(self):
        return f"{self.academic_year} | Year {self.year} Sem {self.semester}"

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("course", "academic_year", "semester")

    def __str__(self):
        return f"{self.course} | {self.academic_year} | Sem {self.semester.semester}"

class FacultyAssignment(models.Model):
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "FACULTY"}
    )
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("faculty", "offering")

    def __str__(self):
        return f"{self.faculty} → {self.offering}"

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "STUDENT"}
    )
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)

    is_repeat = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "offering")

    def __str__(self):
        return f"{self.student} - {self.offering}"
