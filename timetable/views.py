from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from academics.models import Enrollment, FacultyAssignment
from .models import TimetableEntry

@login_required
def student_timetable(request):
    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not allowed")

    enrollments = Enrollment.objects.filter(
        student=request.user,
        is_active=True
    )

    timetable_entries = TimetableEntry.objects.filter(
        offering__in=enrollments.values("offering")
    ).select_related(
        "offering__course",
        "timeslot"
    ).order_by(
        "day", "timeslot__start_time"
    )

    return render(
        request,
        "student/timetable.html",
        {"timetable_entries": timetable_entries}
    )

@login_required
def faculty_timetable(request):
    if not hasattr(request.user, "facultyprofile"):
        return HttpResponseForbidden("Not allowed")

    assignments = FacultyAssignment.objects.filter(
        faculty=request.user,
        is_active=True
    )

    timetable_entries = TimetableEntry.objects.filter(
        offering__in=assignments.values("offering")
    ).select_related(
        "offering__course",
        "timeslot"
    ).order_by(
        "day", "timeslot__start_time"
    )

    return render(
        request,
        "faculty/timetable.html",
        {"timetable_entries": timetable_entries}
    )