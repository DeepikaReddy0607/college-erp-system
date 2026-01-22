from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from academics.models import CourseOffering, FacultyAssignment
from grades.models import FinalGrade, GradeApproval, GradeComputation, MarksEntryWindow, MarksSubmission
from accounts.utils import is_faculty, is_hod, is_student
from grades.utils import calculate_cgpa, calculate_sgpa

User = get_user_model()

@login_required
def faculty_submit_marks(request, offering_id):
    if not is_faculty(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    if not FacultyAssignment.objects.filter(
        faculty=request.user,
        offering=offering,
        is_active=True
    ).exists():
        return HttpResponseForbidden()

    active_window = MarksEntryWindow.objects.filter(
        course_offering=offering,
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).first()

    active_phase = active_window.phase if active_window else None

    students = User.objects.filter(
        studentprofile__isnull=False,
        enrollment__offering=offering,
        enrollment__is_active=True
    ).select_related("studentprofile")

    if request.method == "POST":
        if not active_phase:
            return HttpResponseForbidden("Marks entry window is closed.")

        for student in students:
            value = request.POST.get(f"{active_phase}_{student.id}")
            if value is None:
                continue

            submission, _ = MarksSubmission.objects.get_or_create(
                student=student,
                course_offering=offering,
                defaults={"submitted_by": request.user}
            )

            if submission.is_locked:
                continue

            setattr(submission, active_phase, value)
            submission.save()

        if "final_submit" in request.POST:
            for submission in MarksSubmission.objects.filter(
                course_offering=offering
            ):
                if not submission.is_locked:
                    submission.submit()

        return redirect("faculty_submit_marks", offering_id=offering.id)

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
            "active_phase": active_phase,
            "active_window": active_window,
        }
    )

@login_required
def hod_review_computed_grades(request, offering_id):
    if not is_hod(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    computed = GradeComputation.objects.filter(
        course_offering=offering
    ).select_related("student")

    if request.method == "POST":
        for cg in computed:
            if request.POST.get(f"approve_{cg.student.id}"):
                approval, _ = GradeApproval.objects.get_or_create(
                    student=cg.student,
                    course_offering=offering,
                    defaults={"approved_by": request.user}
                )
                if not approval.is_approved:
                    approval.is_approved = True
                    approval.save()

        return redirect("hod_review_grades", offering_id=offering.id)

    approvals = {
        a.student_id: a
        for a in GradeApproval.objects.filter(course_offering=offering)
    }

    return render(
        request,
        "faculty/review_grades.html",
        {
            "offering": offering,
            "computed_grades": computed,
            "approvals": approvals,
        }
    )

@login_required
def hod_publish_and_freeze_grades(request, offering_id):
    if not is_hod(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    if FinalGrade.objects.filter(
        course_offering=offering,
        is_frozen=True
    ).exists():
        return HttpResponseForbidden("Grades already frozen.")

    approvals = GradeApproval.objects.filter(
        course_offering=offering,
        is_approved=True
    ).select_related("student")

    if request.method == "POST":
        for approval in approvals:
            cg = GradeComputation.objects.get(
                student=approval.student,
                course_offering=offering
            )

            fg, _ = FinalGrade.objects.get_or_create(
                student=approval.student,
                course_offering=offering,
                defaults={
                    "final_grade": cg.computed_grade,
                    "published_by": request.user
                }
            )

            if not fg.is_frozen:
                fg.freeze()

        return redirect("hod_dashboard")

    return render(
        request,
        "faculty/publish_grades.html",
        {
            "offering": offering,
            "approved_grades": approvals
        }
    )

@login_required
def student_view_grades(request):
    if not is_student(request.user):
        return HttpResponseForbidden()

    semester = request.GET.get("semester")

    grades = FinalGrade.objects.filter(
        student=request.user,
        is_frozen=True
    ).select_related("course_offering__course")

    if semester:
        grades = grades.filter(course_offering__semester=semester)

    sgpa = calculate_sgpa(request.user, semester) if semester else None
    cgpa = calculate_cgpa(request.user)

    return render(
        request,
        "student/grades.html",
        {
            "grades": grades,
            "sgpa": sgpa,
            "cgpa": cgpa,
            "selected_semester": semester,
        }
    )
