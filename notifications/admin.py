from django.contrib import admin
from .models import Notification, NotificationRecipient

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "notification_type", "sender", "created_at")
    search_fields = ("title", "message")
    list_filter = ("notification_type", "created_at")


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ("notification", "user", "is_read", "read_at")
    list_filter = ("is_read",)