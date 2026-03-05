from django.db import models
from django.conf import settings


class Event(models.Model):

    CLUB_CHOICES = [
        ('CSEA', 'CSEA'),
        ('Coding Club', 'Coding Club'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Registration Open'),
        ('closed', 'Registration Closed'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    club = models.CharField(max_length=50, choices=CLUB_CHOICES)
    event_type = models.CharField(max_length=100)  # Workshop, Seminar, Hackathon

    banner = models.ImageField(upload_to="event_banners/", blank=True, null=True)

    date = models.DateField()
    time = models.TimeField()

    venue = models.CharField(max_length=200, blank=True, null=True)
    online_link = models.URLField(blank=True, null=True)

    registration_deadline = models.DateTimeField()
    total_seats = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_events'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    def seats_filled(self):
        return self.registrations.count()

    def seats_remaining(self):
        return self.total_seats - self.seats_filled()

    def is_registration_open(self):
        from django.utils import timezone
        return (
            self.status == 'open' and
            timezone.now() < self.registration_deadline and
            self.seats_remaining() > 0
        )
    def __str__(self):
        return self.title
    
class EventRegistration(models.Model):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'student')
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['student']),
        ]
    def __str__(self):
        return f"{self.student} - {self.event}"

class EventAttendance(models.Model):

    registration = models.OneToOneField(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name='attendance'
    )

    attended = models.BooleanField(default=False)

    marked_at = models.DateTimeField(blank=True, null=True)

class EventCertificate(models.Model):

    registration = models.OneToOneField(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name='certificate'
    )

    certificate_file = models.FileField(upload_to='event_certificates/')
    issued_at = models.DateTimeField(auto_now_add=True)