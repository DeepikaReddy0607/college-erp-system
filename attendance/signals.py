from django.db.models.signals import post_save
from django.dispatch import receiver
from attendance.models import AttendanceRecord
from notifications.models import Notification, NotificationRecipient


@receiver(post_save, sender=AttendanceRecord)
def check_attendance_shortage(sender, instance, **kwargs):

    percentage = instance.calculate_percentage()

    if percentage < 75:
        notification = Notification.objects.create(
            title="Attendance Warning",
            message=f"Your attendance in {instance.offering.course.name} is below 75%.",
            notification_type="WARNING",
            course_offering=instance.offering
        )

        NotificationRecipient.objects.create(
            notification=notification,
            user=instance.student
        )
