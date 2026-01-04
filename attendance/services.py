from django.utils import timezone
from django.db.models import Count, Q
from attendance.models import AttendanceSession, AttendanceRecord
from academics.models import Enrollment

def auto_lock_expired_sessions(course_offering):
    """
    Automatically locks attendance sessions whose edit window has expired.
    Should be called whenever attendance history is accessed.
    """

    sessions = AttendanceSession.objects.filter(
        course_offering=course_offering,
        status=AttendanceSession.STATUS_OPEN
    )

    now = timezone.now()

    for session in sessions:
        if not session.is_editable():
            session.status = AttendanceSession.STATUS_LOCKED
            session.locked_at = now
            session.save(update_fields=["status", "locked_at"])

def get_course_attendance_stats(course_offering, student):
    """
    Returns attendance statistics for ONE student in ONE course offering.
    """

    # Only sessions that actually exist
    total_sessions = AttendanceSession.objects.filter(
        course_offering=course_offering
    ).count()

    if total_sessions == 0:
        return {
            "total": 0,
            "present": 0,
            "absent": 0,
            "percentage": 0.0,
            "status": "SAFE",
        }

    # Count attendance by status
    status_counts = AttendanceRecord.objects.filter(
        session__course_offering=course_offering,
        student=student
    ).values("status").annotate(count=Count("id"))

    counts = {row["status"]: row["count"] for row in status_counts}

    present = (
        counts.get(AttendanceRecord.STATUS_PRESENT, 0)
        + counts.get(AttendanceRecord.STATUS_LATE, 0)
        + counts.get(AttendanceRecord.STATUS_EXCUSED, 0)
    )

    absent = counts.get(AttendanceRecord.STATUS_ABSENT, 0)

    percentage = (present / total_sessions) * 100

    return {
        "total": total_sessions,
        "present": present,
        "absent": absent,
        "percentage": round(percentage, 2),
        "status": get_attendance_status(percentage),
    }

def get_attendance_status(percentage):
    """
    Institutional attendance policy.
    """

    if percentage >= 75:
        return "SAFE"
    elif percentage >= 65:
        return "RISK"
    return "DETENTION"
def get_student_attendance_summary(student):
    """
    Returns attendance summary for ALL enrolled courses of a student.
    Used in student dashboard.
    """

    summary = []

    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related(
        "offering",
        "offering__course"
    )

    for enrollment in enrollments:
        stats = get_course_attendance_stats(
            enrollment.offering,
            student
        )

        summary.append({
            "course_code": enrollment.offering.course.course_code,
            "course_title": enrollment.offering.course.course_title,
            **stats
        })

    return summary
