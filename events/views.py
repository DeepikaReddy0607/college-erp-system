from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden

from events.models import Event
from accounts.models import StudentProfile   # adjust app name if needed

@login_required
def student_upcoming_events(request):
    student_profile = request.user.studentprofile
    student_year = student_profile.year
    now = timezone.now()

    events = Event.objects.filter(
        is_active=True,
        start_datetime__gte=now
    ).filter(
        Q(is_common=True) |
        Q(year=student_year)
    ).order_by('start_datetime')

    return render(
        request,
        'student/events/student_upcoming_events.html',
        {'events': events}
    )

@login_required
def student_past_events(request):
    student_profile = request.user.studentprofile
    student_year = student_profile.year
    now = timezone.now()

    events = Event.objects.filter(
        is_active=True,
        end_datetime__lt=now
    ).filter(
        Q(is_common=True) |
        Q(year=student_year)
    ).order_by('-end_datetime')

    return render(
        request,
        'student/events/student_past_events.html',
        {'events': events}
    )

@login_required
def student_event_detail(request, event_id):
    student_profile = request.user.studentprofile
    student_year = student_profile.year

    event = get_object_or_404(
        Event,
        event_id=event_id,
        is_active=True
    )

    if not (event.is_common or event.year == student_year):
        return HttpResponseForbidden("You are not allowed to view this event.")

    return render(
        request,
        'student/events/student_event_detail.html',
        {'event': event}
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
    events = Event.objects.all().order_by('-created_at')
    return render(
        request,
        'events/admin_event_list.html',
        {'events': events}
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
