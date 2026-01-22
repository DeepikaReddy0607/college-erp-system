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
