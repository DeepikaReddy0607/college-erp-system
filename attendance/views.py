import csv
from urllib import request
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from accounts.decorators import faculty_required, student_required
from academics.models import CourseOffering, Enrollment
from attendance.models import (
    AttendanceSession,
    AttendanceRecord,
    AttendanceEditLog
)
from attendance.services import auto_lock_expired_sessions, get_student_attendance_summary, get_course_attendance_stats, get_students_below_threshold

@faculty_required
def faculty_attendance_landing(request):
    offerings = CourseOffering.objects.filter(
        facultyassignment__faculty=request.user,
        is_active=True
    ).select_related("course", "semester", "academic_year")

    return render(request, "dashboard/faculty_attendance_landing.html", {
        "offerings": offerings
    })

from django.db import transaction

@faculty_required
def mark_attendance(request, offering_id):
    offering = get_object_or_404(
        CourseOffering,
        id=offering_id,
        facultyassignment__faculty=request.user
    )

    students = Enrollment.objects.filter(
        offering=offering
    ).select_related("student")

    if request.method == "POST":

        session_date = request.POST["date"]
        start_time = request.POST["start_time"]
        end_time = request.POST["end_time"]

        if session_date > str(timezone.now().date()):
            messages.error(request, "Cannot mark attendance for future dates.")
            return redirect("attendance:faculty_attendance")

        if not students.exists():
            return render(request, "dashboard/faculty_attendance.html", {
                "offering": offering,
                "students": students,
                "error": "No students enrolled in this course.",
                "today": timezone.now().date()
            })

        session, created = AttendanceSession.objects.get_or_create(
            course_offering=offering,
            faculty=request.user,
            date=session_date,
            start_time=start_time,
            defaults={"end_time": end_time}
        )

        if AttendanceRecord.objects.filter(session=session).exists():
            messages.error(request, "Attendance already marked for this session.")
            return redirect("attendance:attendance_history", offering_id=offering.id)

        records = []

        for enrollment in students:

            status = request.POST.get(
                f"status_{enrollment.student.id}",
                AttendanceRecord.STATUS_ABSENT
            )

            records.append(
                AttendanceRecord(
                    session=session,
                    student=enrollment.student,
                    status=status
                )
            )

        with transaction.atomic():
            AttendanceRecord.objects.bulk_create(records)

        messages.success(request, "Attendance marked successfully.")

        return redirect(
            "attendance:attendance_history",
            offering_id=offering.id
        )

    return render(request, "dashboard/faculty_attendance.html", {
        "offering": offering,
        "students": students,
        "today": timezone.now().date()
    })

@faculty_required
def attendance_history(request, offering_id):
    faculty = request.user

    offering = get_object_or_404(
        CourseOffering,
        id=offering_id,
        facultyassignment__faculty=faculty
    )

    sessions = AttendanceSession.objects.filter(
        course_offering=offering
    ).order_by("-date", "-start_time")

    session_data = []

    for session in sessions:

        # auto lock expired sessions
        if not session.is_editable() and session.status != AttendanceSession.STATUS_LOCKED:
            session.lock()

        session_data.append({
            "obj": session,
            "editable": session.is_editable()
        })

    return render(
        request,
        "dashboard/faculty_attendance_history.html",
        {
            "offering": offering,
            "sessions": session_data
        }
    )



@faculty_required
def edit_attendance(request, session_id):
    faculty = request.user

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        faculty=faculty
    )

    records = AttendanceRecord.objects.filter(
        session=session
    ).select_related("student")

    if not session.is_editable():
        return render(request, "dashboard/faculty_attendance_edit.html", {
            "session": session,
            "records": records,
            "error": "Attendance is locked and cannot be edited."
        })
    
    if request.method == "POST":
        for record in records:
            new_status = request.POST.get(f"status_{record.student.id}")

            if new_status and new_status != record.status:
                AttendanceEditLog.objects.create(
                    attendance_record=record,
                    edited_by=faculty,
                    old_status=record.status,
                    new_status=new_status,
                    reason=request.POST.get("reason", "")
                )

                record.status = new_status
                record.save(update_fields=["status"])
        messages.success(request, "Attendance updated successfully.")
        return redirect(
            "attendance:attendance_history",
            offering_id=session.course_offering.id
        )

    return render(request, "dashboard/faculty_attendance_edit.html", {
        "session": session,
        "records": records
    })

@student_required
def student_attendance_view(request):
    summary = get_student_attendance_summary(request.user)

    return render(
        request,
        "student/student_attendance.html",
        {"summary": summary}
    )
@faculty_required
def export_attendance_csv(request, offering_id):
    offering = get_object_or_404(
        CourseOffering,
        id=offering_id,
        facultyassignment__faculty=request.user
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{offering.course.course_code}_attendance.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Roll No",
        "Student Name",
        "Present",
        "Absent",
        "Percentage",
        "Status"
    ])

    enrollments = Enrollment.objects.filter(
        offering=offering
    ).select_related("student")

    for enrollment in enrollments:
        student = enrollment.student
        stats = get_course_attendance_stats(offering, student)

        writer.writerow([
            student.username,
            student.get_full_name(),
            stats["present"],
            stats["absent"],
            stats["percentage"],
            stats["status"],
        ])

    return response
