from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import Event, EventRegistration

@login_required
def student_upcoming_events(request):
    today = timezone.now().date()

    events = Event.objects.filter(
        date__gte=today,
        status__in=["open", "closed"]
    ).order_by("date")

    return render(
        request,
        "student/events/event_list.html",
        {"events": events}
    )

@login_required
def student_past_events(request):
    today = timezone.now().date()

    events = Event.objects.filter(
        date__lt=today,
        status__in=["completed", "archived"]
    ).order_by("-date")

    return render(
        request,
        "student/events/event_list.html",
        {"events": events}
    )

@login_required
def student_event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)

    is_registered = EventRegistration.objects.filter(
        event=event,
        student=request.user
    ).exists()

    context = {
        "event": event,
        "is_registered": is_registered,
    }

    return render(
        request,
        "student/events/event_detail.html",
        context
    )

@login_required
def faculty_events(request):
    events = Event.objects.filter(
        is_active=True
    ).order_by('-start_datetime')

    return render(
        request,
        'events/faculty_events.html',
        {'events': events}
    )

@login_required
def admin_event_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed.")

    events = Event.objects.all().order_by("-created_at")

    return render(
        request,
        "events/admin/event_list.html",
        {"events": events}
    )

@login_required
def admin_disable_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    event.is_active = False
    event.save()
    return redirect('admin_event_list')

@login_required
def admin_create_event(request):
    # OPTIONAL: add role check if you have roles
    # if request.user.role != 'ADMIN':
    #     return HttpResponseForbidden("Not allowed")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_type = request.POST.get('event_type')
        organizer = request.POST.get('organizer')
        year = request.POST.get('year')
        is_common = request.POST.get('is_common') == 'on'
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        venue = request.POST.get('venue')
        registration_link = request.POST.get('registration_link')

        # 🔒 YEAR / COMMON VALIDATION
        if is_common:
            year = None
        else:
            if not year:
                messages.error(request, "Please select an academic year or mark the event as common.")
                return render(request, 'events/admin_create_event.html')

        try:
            event = Event(
                title=title,
                description=description,
                event_type=event_type,
                organizer=organizer,
                year=year,
                is_common=is_common,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                venue=venue,
                registration_link=registration_link,
                created_by=request.user
            )

            # This triggers model-level validation (clean())
            event.full_clean()
            event.save()

            messages.success(request, "Event created successfully.")
            return redirect('admin_event_list')

        except ValidationError as e:
            messages.error(request, e.message_dict if hasattr(e, 'message_dict') else e)

    return render(request, 'events/admin_create_event.html')

@login_required
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if not event.is_registration_open():
        messages.error(request, "Registration is closed.")
        return redirect("events:student_event_detail", pk=pk)

    if EventRegistration.objects.filter(event=event, student=request.user).exists():
        messages.warning(request, "You are already registered.")
        return redirect("events:student_event_detail", pk=pk)

    EventRegistration.objects.create(
        event=event,
        student=request.user
    )

    messages.success(request, "Successfully registered.")
    return redirect("events:student_event_detail", pk=pk)

@login_required
def cancel_registration(request, pk):
    event = get_object_or_404(Event, pk=pk)

    registration = EventRegistration.objects.filter(
        event=event,
        student=request.user
    ).first()

    if registration:
        registration.delete()
        messages.success(request, "Registration cancelled.")

    return redirect("events:student_event_detail", pk=pk)

@login_required
def my_events(request):
    registrations = EventRegistration.objects.filter(
        student=request.user
    ).select_related("event").order_by("-registered_at")

    return render(
        request,
        "student/events/my_events.html",
        {"registrations": registrations}
    )