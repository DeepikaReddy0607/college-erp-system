from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from academics.models import CourseOffering
from .models import Notification, NotificationRecipient
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from accounts.utils import is_hod
from django.db.models import Q
User = get_user_model()

@login_required
def faculty_send_notification(request):

    # Faculty guard
    if not hasattr(request.user, "facultyprofile"):
        return redirect("student_dashboard")

    faculty_profile = request.user.facultyprofile
    hod = is_hod(request.user)

    # Get subjects handled by faculty
    faculty_course_offerings = CourseOffering.objects.filter(
        facultyassignment__faculty=request.user,
        facultyassignment__is_active=True
    ).distinct()

    if request.method == "POST":

        title = request.POST.get("title")
        message = request.POST.get("message")
        notification_type = request.POST.get("notification_type")
        course_offering_id = request.POST.get("course_offering_id")
        recipient_scope = request.POST.get("recipient_scope")

        # Validate course offering belongs to this faculty
        course_offering = get_object_or_404(
            CourseOffering,
            id=course_offering_id,
            facultyassignment__faculty=request.user,
            facultyassignment__is_active=True
        )

        # Create notification linked to course offering
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            sender=request.user,
            course_offering=course_offering
        )

        # --------------------------------
        # RECIPIENT LOGIC (Professional)
        # --------------------------------

        if recipient_scope == "students":
            # Students enrolled in this subject
            recipients = User.objects.filter(
                enrollment__offering=course_offering,
                enrollment__is_active = True
            ).distinct()

        elif recipient_scope == "department" and hod:
            # Entire department students
            recipients = User.objects.filter(
                studentprofile__department=faculty_profile.department
            )

        else:
            return redirect("faculty_send_notification")

        # Create delivery entries
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
        {
            "is_hod": hod,
            "faculty_course_offerings": faculty_course_offerings
        }
    )

@login_required
def student_notifications(request):

    notifications = (
        NotificationRecipient.objects
        .select_related("notification", "notification__sender")
        .filter(user=request.user)
        .order_by("-notification__created_at")
    )

    filter_type = request.GET.get("type")

    if filter_type == "unread":
        notifications = notifications.filter(is_read=False)

    elif filter_type in ["INFO", "WARNING", "CRITICAL"]:
        notifications = notifications.filter(
            notification__notification_type=filter_type
        )

    unread_count = notifications.filter(is_read=False).count()

    return render(
        request,
        "student/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count
        }
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
        .order_by("-notification__created_at")
    )

    filter_type = request.GET.get("type")

    if filter_type == "unread":
        notifications = notifications.filter(is_read=False)

    elif filter_type in ["INFO", "WARNING", "CRITICAL"]:
        notifications = notifications.filter(
            notification__notification_type=filter_type
        )

    unread_count = notifications.filter(is_read=False).count()

    return render(
        request,
        "faculty/faculty_notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count
        }
    )
