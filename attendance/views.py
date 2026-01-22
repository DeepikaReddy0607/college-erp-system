import csv
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
from attendance.services import auto_lock_expired_sessions, get_student_attendance_summary, get_course_attendance_stats

@faculty_required
def faculty_attendance_landing(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    offerings = CourseOffering.objects.filter(
        facultyassignment__faculty=request.user,
        is_active=True
    ).select_related("course", "semester", "academic_year")

    return render(request, "dashboard/faculty_attendance_landing.html", {
        "offerings": offerings
    })

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
        session, created = AttendanceSession.objects.get_or_create(
            course_offering=offering,
            faculty=request.user,
            date=request.POST["date"],
            start_time=request.POST["start_time"],
            defaults={"end_time": request.POST["end_time"]}
        )

        if not created:
            return render(request, "dashboard/faculty_attendance_mark.html", {
                "offering": offering,
                "students": students,
                "error": "Attendance already marked."
            })

        records = [
            AttendanceRecord(
                session=session,
                student=enrollment.student,
                status=request.POST.get(
                    f"status_{enrollment.student.id}", "absent"
                )
            )
            for enrollment in students
        ]

        AttendanceRecord.objects.bulk_create(records)

        return redirect("faculty_attendance_history", offering_id=offering.id)

    return render(request, "dashboard/faculty_attendance.html", {
        "offering": offering,
        "students": students,
        "today": timezone.now().date()
    })

@faculty_required
def attendance_history(request, offering_id):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    faculty = request.user

    offering = get_object_or_404(
        CourseOffering,
        id=offering_id,
        facultyassignment__faculty=faculty
    )

    auto_lock_expired_sessions(offering)

    sessions = AttendanceSession.objects.filter(
        course_offering=offering
    ).order_by("-date", "-start_time")

    return render(request, "attendance/attendance_history.html", {
        "offering": offering,
        "sessions": sessions
    })

@faculty_required
def edit_attendance(request, session_id):
    faculty = request.user

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        faculty=faculty
    )

    if not session.is_editable():
        return render(request, "attendance/edit_attendance.html", {
            "session": session,
            "records": records,
            "error": "Attendance is locked and cannot be edited."
        })
    records = AttendanceRecord.objects.filter(
        session=session
    ).select_related("student")

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
                record.save()

        return redirect(
            "attendance_history",
            offering_id=session.course_offering.id
        )

    return render(request, "dashboard/faculty_attendance_edit.html", {
        "session": session,
        "records": records
    })

@student_required
def student_attendance_view(request):
    if request.user.role != "STUDENT":
        return redirect("dashboard")

    summary = get_student_attendance_summary(request.user)

    return render(
        request,
        "student/student_attendance.html",
        {"summary": summary}
    )
@faculty_required
def export_attendance_csv(request, offering_id):
    if request.user.role != "FACULTY":
        return HttpResponse("Unauthorized", status=403)
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