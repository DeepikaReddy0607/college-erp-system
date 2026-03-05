from grades.models import FinalGrade


def calculate_sgpa(student, semester):
    grades = FinalGrade.objects.filter(
        student=student,
        is_frozen=True,
        course_offering__semester=semester
    ).select_related("course_offering__course")

    total_credits = 0
    weighted_sum = 0

    for g in grades:
        credits = g.course_offering.course.credits
        if not credits:
            continue
        total_credits += credits
        weighted_sum += credits * g.grade_point

    if total_credits == 0:
        return None

    return round(weighted_sum / total_credits, 2)


def calculate_cgpa(student):
    grades = FinalGrade.objects.filter(
        student=student,
        is_frozen=True
    ).select_related("course_offering__course")

    total_credits = 0
    weighted_sum = 0

    for g in grades:
        credits = g.course_offering.course.credits
        if not credits:
            continue
        total_credits += credits
        weighted_sum += credits * g.grade_point

    if total_credits == 0:
        return None

    return round(weighted_sum / total_credits, 2)

import statistics
from grades.models import GradeComputation, MarksSubmission, GRADE_POINTS

def compute_relative_grades(offering, computed_by):

    submissions = MarksSubmission.objects.filter(
        course_offering=offering,
        is_locked=True
    )

    totals = [s.total for s in submissions]

    if not totals:
        return

    mean = statistics.mean(totals)
    std = statistics.pstdev(totals) if len(totals) > 1 else 1

    for submission in submissions:
        z = (submission.total - mean) / std

        # Standard relative mapping
        if z >= 1.5:
            grade = "Ex"
        elif z >= 1.0:
            grade = "A"
        elif z >= 0.5:
            grade = "B"
        elif z >= 0:
            grade = "C"
        elif z >= -0.5:
            grade = "D"
        elif z >= -1:
            grade = "P"
        else:
            grade = "F"

        GradeComputation.objects.update_or_create(
            student=submission.student,
            course_offering=offering,
            defaults={
                "computed_grade": grade,
                "computed_by_exam_section": True,
                "remarks": f"Mean={mean:.2f}, Std={std:.2f}"
            }
        ) 