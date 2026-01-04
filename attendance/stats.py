from datetime import timedelta
from django.utils import timezone
from attendance.models import AttendanceSession, AttendanceRecord
from academics.models import Enrollment

DETENTION_THRESHOLD = 75


def get_course_attendance_stats(course_offering, student):
    """
    Returns attendance statistics for a student in a course offering.
    """

    total_sessions = AttendanceSession.objects.filter(
        course_offering=course_offering
    ).count()

    present_count = AttendanceRecord.objects.filter(
        session__course_offering=course_offering,
        student=student,
        status="present"
    ).count()

    absent_count = AttendanceRecord.objects.filter(
        session__course_offering=course_offering,
        student=student,
        status="absent"
    ).count()

    percentage = (
        (present_count / total_sessions) * 100
        if total_sessions > 0 else 0
    )

    return {
        "total_classes": total_sessions,
        "present": present_count,
        "absent": absent_count,
        "percentage": round(percentage, 2),
        "is_detained": percentage < DETENTION_THRESHOLD
    }


def is_student_detained(course_offering, student):
    return get_course_attendance_stats(course_offering, student)["is_detained"]


def get_students_below_threshold(course_offering, threshold=DETENTION_THRESHOLD):
    """
    Optimized: returns list of students below attendance threshold
    """

    students = []

    enrolled_students = Enrollment.objects.filter(
        offering=course_offering
    ).select_related("student")

    for enrollment in enrolled_students:
        student = enrollment.student
        stats = get_course_attendance_stats(course_offering, student)

        if stats["percentage"] < threshold:
            students.append({
                "student": student,
                "percentage": stats["percentage"]
            })

    return students


def get_student_attendance_summary(student):
    """
    Used for student dashboard
    """

    summary = []

    enrollments = Enrollment.objects.filter(student=student)\
        .select_related("offering", "offering__course")

    for enrollment in enrollments:
        stats = get_course_attendance_stats(
            enrollment.offering,
            student
        )

        summary.append({
            "course": enrollment.offering.course.course_title,
            "course_code": enrollment.offering.course.course_code,
            **stats
        })

    return summary
