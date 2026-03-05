from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from academics.models import CourseOffering
from grades.models import MarksSubmission, FinalGrade, SemesterResult
from accounts.utils import is_faculty, is_student, is_exam_section

User = get_user_model()
@login_required
def faculty_submit_marks(request, offering_id):
    if not is_faculty(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    students = User.objects.filter(
        enrollment__offering=offering,
        enrollment__is_active=True
    )

    if request.method == "POST":
        for student in students:
            minor1 = request.POST.get(f"minor1_{student.id}")
            minor2 = request.POST.get(f"minor2_{student.id}")
            mid = request.POST.get(f"mid_{student.id}")
            end = request.POST.get(f"end_{student.id}")

            submission, _ = MarksSubmission.objects.get_or_create(
                student=student,
                course_offering=offering,
                defaults={"submitted_by": request.user}
            )

            if submission.is_locked:
                continue
            def safe_decimal(value):
                if value in [None, "", "None"]:
                    return None
                return value
            submission.minor1 = safe_decimal(minor1) or submission.minor1
            submission.minor2 = safe_decimal(minor2) or submission.minor2
            submission.mid = safe_decimal(mid) or submission.mid
            submission.end = safe_decimal(end) or submission.end
            submission.submitted_by = request.user
            submission.save()

        if "lock_marks" in request.POST:
            if "lock_marks" in request.POST:
                submissions = MarksSubmission.objects.filter(course_offering=offering)
            for s in submissions:
                s.lock()

        return redirect("grades:faculty_submit_marks", offering_id=offering.id)

    submissions = {
        m.student_id: m
        for m in MarksSubmission.objects.filter(course_offering=offering)
    }

    return render(
        request,
        "faculty/submit_marks.html",
        {
            "offering": offering,
            "students": students,
            "submissions": submissions,
        }
    )

@login_required
def exam_upload_final_grades(request, offering_id):
    if not is_exam_section(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    submissions = MarksSubmission.objects.filter(
        course_offering=offering,
        is_locked=True
    ).select_related("student")

    if request.method == "POST":
        for submission in submissions:
            grade_letter = request.POST.get(f"grade_{submission.student.id}")

            if not grade_letter:
                continue

            FinalGrade.objects.update_or_create(
                student=submission.student,
                course_offering=offering,
                defaults={
                    "grade_letter": grade_letter,
                    "published_by": request.user
                }
            )

        return redirect("exam_upload_final_grades", offering_id=offering.id)

    return render(
        request,
        "exam/upload_final_grades.html",
        {
            "offering": offering,
            "submissions": submissions,
        }
    )

@login_required
def exam_upload_semester_results(request, semester_id):
    if not is_exam_section(request.user):
        return HttpResponseForbidden()

    from academics.models import Semester
    semester = get_object_or_404(Semester, id=semester_id)

    students = User.objects.filter(
        enrollment__offering__semester=semester
    ).distinct()

    if request.method == "POST":
        for student in students:
            sgpa = request.POST.get(f"sgpa_{student.id}")
            cgpa = request.POST.get(f"cgpa_{student.id}")

            if not sgpa and not cgpa:
                continue

            SemesterResult.objects.update_or_create(
                student=student,
                semester=semester,
                defaults={
                    "sgpa": sgpa,
                    "cgpa": cgpa,
                    "published_by": request.user
                }
            )

        return redirect("exam_upload_semester_results", semester_id=semester.id)

    return render(
        request,
        "exam/upload_semester_results.html",
        {
            "semester": semester,
            "students": students,
        }
    )

@login_required
def exam_freeze_results(request, offering_id):
    if not is_exam_section(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    if request.method == "POST":
        FinalGrade.objects.filter(
            course_offering=offering
        ).update(is_frozen=True)

        return redirect("exam_dashboard")

    return render(
        request,
        "exam/confirm_freeze.html",
        {"offering": offering}
    )

@login_required
def student_view_grades(request):
    if not is_student(request.user):
        return HttpResponseForbidden()

    semester_id = request.GET.get("semester")

    grades = FinalGrade.objects.filter(
        student=request.user,
        is_frozen=True
    ).select_related("course_offering__course")

    if semester_id:
        grades = grades.filter(course_offering__semester_id=semester_id)

    semester_result = None
    if semester_id:
        semester_result = SemesterResult.objects.filter(
            student=request.user,
            semester_id=semester_id,
            is_locked=True
        ).first()

    return render(
        request,
        "student/grades.html",
        {
            "grades": grades,
            "semester_result": semester_result,
            "selected_semester": semester_id,
        }
    )