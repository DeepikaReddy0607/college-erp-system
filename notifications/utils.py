from .models import Notification

def notify(user, message):
    Notification.objects.create(
        sender=user,
        message=message
    )
