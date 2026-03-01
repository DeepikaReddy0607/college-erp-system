from notifications.models import NotificationRecipient

def unread_notifications(request):
    if request.user.is_authenticated:
        count = NotificationRecipient.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {"unread_notifications_count": count}
    return {}
