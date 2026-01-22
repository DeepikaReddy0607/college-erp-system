from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Notification, NotificationRecipient
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from accounts.utils import is_hod
User = get_user_model()

@login_required
def faculty_send_notification(request):
    # faculty guard
    if not hasattr(request.user, "facultyprofile"):
        return redirect("student_dashboard")

    faculty_profile = request.user.facultyprofile
    hod = is_hod(request.user)

    if request.method == "POST":
        title = request.POST["title"]
        message = request.POST["message"]
        notification_type = request.POST["notification_type"]
        recipient_type = request.POST["recipient_type"]

        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            sender=request.user
        )

        # 👇 RECIPIENT LOGIC
        if recipient_type == "students":
            recipients = User.objects.filter(
                studentprofile__department=faculty_profile.department
            )

        elif recipient_type == "faculty" and hod:
            recipients = User.objects.filter(
                facultyprofile__department=faculty_profile.department
            )

        else:
            return redirect("faculty_send_notification")

        NotificationRecipient.objects.bulk_create([
            NotificationRecipient(
                notification=notification,
                user=user
            )
            for user in recipients
        ])

        return redirect("faculty_send_notification")

    return render(
        request,
        "faculty/send_notifications.html",
        {"is_hod": hod}
    )

@login_required
def student_notifications(request):
    notifications = (
        NotificationRecipient.objects
        .select_related("notification", "notification__sender")
        .filter(user=request.user)
    )

    filter_type = request.GET.get("type")

    if filter_type == "unread":
        notifications = notifications.filter(is_read=False)
    elif filter_type in ["INFO", "WARNING", "CRITICAL"]:
        notifications = notifications.filter(
            notification__notification_type=filter_type
        )

    return render(
        request,
        "student/notifications.html",
        {"notifications": notifications}
    )

@login_required
def mark_notification_read(request, pk):
    nr = get_object_or_404(
        NotificationRecipient,
        pk=pk,
        user=request.user
    )
    nr.mark_as_read()
    return redirect("student_notifications")

@login_required
def ajax_mark_notification_read(request, pk):
    if request.method == "POST":
        nr = get_object_or_404(
            NotificationRecipient,
            pk=pk,
            user=request.user
        )
        nr.mark_as_read()

        unread_count = NotificationRecipient.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return JsonResponse({
            "success": True,
            "unread_count": unread_count
        })

    return JsonResponse({"success": False}, status=400)

@login_required
def faculty_notifications(request):
    if not hasattr(request.user, "facultyprofile"):
        return redirect("student_dashboard")

    notifications = (
        NotificationRecipient.objects
        .select_related("notification", "notification__sender")
        .filter(user=request.user)
    )

    filter_type = request.GET.get("type")

    if filter_type == "unread":
        notifications = notifications.filter(is_read=False)
    elif filter_type in ["INFO", "WARNING", "CRITICAL"]:
        notifications = notifications.filter(
            notification__notification_type=filter_type
        )

    return render(
        request,
        "faculty/faculty_notifications.html",
        {"notifications": notifications}
    )
