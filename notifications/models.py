from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    NOTIFICATION_TYPE_CHOICES = [
        (INFO, "Info"),
        (WARNING, "Warning"),
        (CRITICAL, "Critical"),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()

    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications"
    )

    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPE_CHOICES,
        default=INFO
    )

    link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class NotificationRecipient(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="recipients"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("notification", "user")

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
            
    def __str__(self):
        return f"{self.user} → {self.notification}"
