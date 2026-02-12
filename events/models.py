from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('EVENT', 'Event'),
        ('WORKSHOP', 'Workshop'),
    ]

    ORGANIZER_CHOICES = [
        ('CSEA', 'CSEA'),
        ('CODING_CLUB', 'Coding Club'),
    ]

    event_id = models.BigAutoField(primary_key=True)

    title = models.CharField(max_length=200)
    description = models.TextField()

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES
    )

    organizer = models.CharField(
        max_length=30,
        choices=ORGANIZER_CHOICES
    )

    # Academic year: 1 / 2 / 3 / 4
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Applicable academic year (1–4) if not common"
    )

    # True → visible to all years
    is_common = models.BooleanField(default=False)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    venue = models.CharField(max_length=150, blank=True)
    registration_link = models.URLField()

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Enforce visibility rule:
        - If event is common → year must be NULL
        - If event is not common → year must be provided
        """
        if self.is_common and self.year is not None:
            raise ValidationError("Common events must not have a year assigned.")

        if not self.is_common and self.year is None:
            raise ValidationError("Non-common events must have a year assigned.")

    def __str__(self):
        return self.title
