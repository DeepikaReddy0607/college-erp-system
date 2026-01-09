
from grades.models import StudentGrade


def calculate_sgpa(student, semester):
    records = StudentGrade.objects.filter(
        student=student,
        subject__semester=semester
    ).select_related("subject")

    total_points = 0
    total_credits = 0

    for r in records:
        total_points += r.grade_point * r.subject.credits
        total_credits += r.subject.credits

    return round(total_points / total_credits, 2) if total_credits else 0

def calculate_cgpa(student):
    records = StudentGrade.objects.select_related("subject").filter(student=student)

    total_points = 0
    total_credits = 0

    for r in records:
        total_points += r.grade_point * r.subject.credits
        total_credits += r.subject.credits

    return round(total_points / total_credits, 2) if total_credits else 0

def can_upload_grades(user, subject):
    if hasattr(user, "facultyprofile"):
        return True  
    return False
