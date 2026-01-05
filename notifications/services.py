from .models import Notification, NotificationRecipient


def send_notification(
    *,
    title,
    message,
    recipients,
    sender=None,
    link=None,
    notification_type=Notification.INFO
):
    """
    Central notification creator.
    recipients → queryset or list of User objects
    """

    notification = Notification.objects.create(
        title=title,
        message=message,
        sender=sender,
        link=link,
        notification_type=notification_type,
    )

    NotificationRecipient.objects.bulk_create([
        NotificationRecipient(
            notification=notification,
            user=user
        )
        for user in recipients
    ])

    return notification
