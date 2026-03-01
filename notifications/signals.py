from django.db.models.signals import post_save
from django.dispatch import receiver
from assignments.models import Assignment
from notifications.models import Notification, NotificationRecipient
from academics.models import Enrollment


@receiver(post_save, sender=Assignment)
def notify_assignment_created(sender, instance, created, **kwargs):

    if not created:
        return

    # Create notification
    notification = Notification.objects.create(
        title=f"New Assignment: {instance.title}",
        message=f"A new assignment has been posted for {instance.offering.course.name}.",
        notification_type="INFO",
        sender=instance.created_by,
        course_offering=instance.offering
    )

    # Get enrolled students
    students = Enrollment.objects.filter(
        offering=instance.offering,
        is_active=True
    ).values_list("student", flat=True)

    # Create recipient entries
    NotificationRecipient.objects.bulk_create([
        NotificationRecipient(
            notification=notification,
            user_id=student_id
        )
        for student_id in students
    ])

@receiver(post_save, sender=Assignment)
def auto_notify_assignment_created(sender, instance, created, **kwargs):

    if not created:
        return

    # Create notification
    notification = Notification.objects.create(
        title=f"New Assignment: {instance.title}",
        message=f"A new assignment has been posted.",
        notification_type="INFO",
        sender=instance.created_by,
        course_offering=instance.offering
    )

    # Get enrolled students
    student_ids = Enrollment.objects.filter(
        offering=instance.offering,
        is_active=True
    ).values_list("student_id", flat=True)

    # Bulk create delivery rows
    NotificationRecipient.objects.bulk_create([
        NotificationRecipient(
            notification=notification,
            user_id=student_id
        )
        for student_id in student_ids
    ])