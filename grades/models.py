from django.db import models
from academics.models import Course
from django.contrib.auth import get_user_model
User = get_user_model()

class StudentGrade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Course, on_delete=models.CASCADE)

    grade = models.CharField(
        max_length=2,
        choices=[
            ("Ex", "Ex"),
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
            ("P", "P"),
            ("M", "M"),  
            ("F", "F"),
            ("X", "X"),
        ]
    )

    grade_point = models.FloatField(default=0)

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_grades"
    )

    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "subject")

    def save(self, *args, **kwargs):
        self.grade_point = self.calculate_grade_point()
        super().save(*args, **kwargs)

    def calculate_grade_point(self):
        grade_map = {
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
        return grade_map[self.grade]

