from django.db import models
from academics.models import CourseOffering

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

class TimetableEntry(models.Model):
    DAYS = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
    ]

    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="timetable_entries"
    )

    day = models.CharField(max_length=3, choices=DAYS)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    room = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ("offering", "day", "timeslot")
        ordering = ["day", "timeslot__start_time"]