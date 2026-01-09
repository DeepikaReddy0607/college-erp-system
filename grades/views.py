from django.http import HttpResponseForbidden
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from academics.models import Course
from django.contrib.auth import get_user_model
from grades.models import StudentGrade
from grades.utils import calculate_cgpa, calculate_sgpa, can_upload_grades
from accounts.utils import is_hod

User = get_user_model()
@login_required
def upload_grades(request, subject_id):
    if not hasattr(request.user, "facultyprofile"):
        return HttpResponseForbidden("Not allowed")

    subject = get_object_or_404(Course, id=subject_id)
    faculty = request.user
    faculty_profile = faculty.facultyprofile

    students = User.objects.filter(
        studentprofile__department=faculty_profile.department
    ).select_related("studentprofile")

    if request.method == "POST":
        for student in students:
            grade_val = request.POST.get(f"grade_{student.id}")
            if not grade_val:
                continue

            grade_obj, created = StudentGrade.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={
                    "grade": grade_val,
                    "uploaded_by": faculty,
                }
            )

            # 🔒 Do not modify locked grades
            if not created and grade_obj.is_locked:
                continue

            grade_obj.grade = grade_val
            grade_obj.uploaded_by = faculty
            grade_obj.save()

        return redirect("upload_grades", subject_id=subject.id)

    grades_map = {
        g.student_id: g
        for g in StudentGrade.objects.filter(subject=subject)
    }

    return render(
        request,
        "faculty/upload_grades.html",
        {
            "subject": subject,
            "students": students,
            "grades_map": grades_map,
        }
    )


@login_required
def student_grades(request):
    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not allowed")

    student = request.user
    student_profile = student.studentprofile

    semester = request.GET.get("semester")
    if semester is None:
        semester = student_profile.current_semester  
    semester = int(semester)

    grades = StudentGrade.objects.select_related("subject").filter(
        student=student,
        subject__semester=semester,
        is_locked=True
    ).order_by("subject__name")

    sgpa = calculate_sgpa(student, semester)
    cgpa = calculate_cgpa(student)

    semesters = (
        StudentGrade.objects
        .filter(student=student,is_locked=True)
        .values_list("subject__semester", flat=True)
        .distinct()
        .order_by("subject__semester")
    )

    return render(
        request,
        "student/grades.html",
        {
            "grades": grades,
            "sgpa": sgpa,
            "cgpa": cgpa,
            "current_semester": semester,
            "semesters": semesters,
        }
    )
