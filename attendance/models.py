from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

User = settings.AUTH_USER_MODEL
class AttendanceSession(models.Model):
    """
    Represents ONE class block (theory or lab).
    """

    STATUS_OPEN = "open"
    STATUS_LOCKED = "locked"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_LOCKED, "Locked"),
    ]

    course_offering = models.ForeignKey(
        "academics.CourseOffering",
        on_delete=models.CASCADE,
        related_name="attendance_sessions"
    )

    faculty = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="faculty_attendance_sessions"
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN
    )

    created_at = models.DateTimeField(auto_now_add=True)
    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (
            "course_offering",
            "date",
            "start_time",
        )
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.course_offering} | {self.date} {self.start_time}"

    def session_end_datetime(self):
        return timezone.make_aware(
            datetime.combine(self.date, self.end_time)
        )

    def is_editable(self):
        """
        Attendance can be edited only within the configured edit window
        AND only if session is open.
        """
        config = AttendanceWindowConfig.get_active_config()
        if not config or self.status != self.STATUS_OPEN:
            return False

        allowed_until = self.session_end_datetime() + timedelta(
            days=config.edit_window_days
        )
        return timezone.now() <= allowed_until

    def lock(self):
        """Lock attendance permanently."""
        if self.status != self.STATUS_LOCKED:
            self.status = self.STATUS_LOCKED
            self.locked_at = timezone.now()
            self.save()
class AttendanceRecord(models.Model):
    """
    Attendance status for each student in a session.
    """

    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"
    STATUS_LATE = "late"
    STATUS_EXCUSED = "excused"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_LATE, "Late"),
        (STATUS_EXCUSED, "Excused"),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student} | {self.session} | {self.status}"
class AttendanceEditLog(models.Model):
    """
    Complete audit trail for attendance edits.
    """

    attendance_record = models.ForeignKey(
        AttendanceRecord,
        on_delete=models.CASCADE,
        related_name="edit_logs"
    )

    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance_edit_actions"
    )

    old_status = models.CharField(max_length=10)
    new_status = models.CharField(max_length=10)

    reason = models.TextField(blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.attendance_record.student} | "
            f"{self.old_status} → {self.new_status}"
        )
class AttendanceWindowConfig(models.Model):
    """
    Controls how long attendance remains editable.
    Singleton-style configuration.
    """

    edit_window_days = models.PositiveIntegerField(default=2)
    active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_active_config(cls):
        return cls.objects.filter(active=True).first()

    def __str__(self):
        return f"Attendance Edit Window: {self.edit_window_days} days"
