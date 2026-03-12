from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from assignments.forms import AssignmentForm
from assignments.models import Assignment, AssignmentSubmission
from accounts.models import FacultyProfile
from academics.models import Course, Enrollment, CourseOffering
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
import zipfile
import os
@login_required
def create_assignment(request):

    # Ensure faculty only
    if not hasattr(request.user, "facultyprofile"):
        return redirect("student_dashboard")

    # Get offerings assigned to this faculty
    faculty_offerings = CourseOffering.objects.filter(
        facultyassignment__faculty=request.user,
        facultyassignment__is_active=True
    ).distinct()

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)

        # Restrict offering choices
        form.fields["offering"].queryset = faculty_offerings

        if form.is_valid():
            assignment = form.save()
            return redirect("faculty_assignments")

    else:
        form = AssignmentForm()
        form.fields["offering"].queryset = faculty_offerings

    return render(
        request,
        "faculty/create_assignment.html",
        {"form": form}
    )

@login_required
def faculty_assignments(request):
    if not hasattr(request.user, "facultyprofile"):
        return redirect("student_dashboard")

    assignments = Assignment.objects.filter(
        offering__facultyassignment__faculty=request.user,
        offering__facultyassignment__is_active=True
    ).select_related("offering__course").distinct()

    assignment_data = []

    for a in assignments:

        total_students = Enrollment.objects.filter(
            offering=a.offering,
            is_active=True
        ).count()

        submitted = AssignmentSubmission.objects.filter(
            assignment=a
        ).count()

        assignment_data.append({
            "assignment": a,
            "submitted": submitted,
            "total": total_students
        })

    return render(
        request,
        "faculty/assignment_list.html",
        {
            "assignment_data": assignment_data,
            "now": timezone.now()
        }
    )

@login_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        offering__facultyassignment__faculty=request.user,
        offering__facultyassignment__is_active=True
    )

    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related("student__user")

    submitted_student_ids = submissions.values_list(
        "student__user_id", flat=True
    )

    not_submitted = Enrollment.objects.filter(
        offering=assignment.offering,
        is_active=True
    ).exclude(
        student_id__in=submitted_student_ids
    ).select_related("student")

    total_students = Enrollment.objects.filter(
        offering=assignment.offering,
        is_active=True
    ).count()


    submitted_count = submissions.count()
    pending_count = total_students - submitted_count

    return render(
        request,
        "faculty/assignment_submissions.html",
        {
            "assignment": assignment,
            "submissions": submissions,
            "not_submitted": not_submitted,
            "total_students": total_students,
            "submitted_count": submitted_count,
            "pending_count": pending_count,
        }
    )

@login_required
def student_assignments(request):
    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not a student account")
    
    student = request.user.studentprofile
    enrollments = Enrollment.objects.filter(
        student=request.user,
        is_active=True
    ).select_related("offering__course")

    offerings = [e.offering for e in enrollments]

    assignments = Assignment.objects.filter(
        offering__in=offerings,
        is_active=True
    ).select_related("offering__course")

    submissions = AssignmentSubmission.objects.filter(student = student)
    submitted_map = {s.assignment_id: s for s in submissions}

    assignment_data = []
    for a in assignments:
        assignment_data.append({
            "assignment": a,
            "submission": submitted_map.get(a.id)
        })

    return render(
        request,
        "student/assignments_list.html",
        {"assignment_data": assignment_data,
         "now": timezone.now(),
         }
    )

@login_required
def submit_assignment(request, assignment_id):
    student = request.user.studentprofile
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if timezone.now() > assignment.due_date:
        return HttpResponseForbidden("Submission deadline has passed.")

    if AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=student
    ).exists():
        return redirect("student_assignments")

    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            is_late = timezone.now() > assignment.due_date
            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                file=file,
                is_late=is_late
            )
            return redirect("student_assignments")

    return render(
        request,
        "student/assignments_submit.html",
        {"assignment": assignment}
    )

@login_required
def grade_submission(request, submission_id):

    submission = get_object_or_404(
        AssignmentSubmission,
        id=submission_id,
        assignment__offering__facultyassignment__faculty=request.user,
        assignment__offering__facultyassignment__is_active=True
    )

    if request.method == "POST":
        marks = request.POST.get("marks")

        if marks:
            submission.marks = marks
            submission.graded_at = timezone.now()
            submission.save()

        return redirect(
            "assignment_submissions",
            assignment_id=submission.assignment.id
        )

@login_required
def edit_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        offering__facultyassignment__faculty=request.user
    )

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)

        if form.is_valid():
            form.save()
            return redirect("faculty_assignments")

    else:
        form = AssignmentForm(instance=assignment)

    return render(request, "faculty/edit_assignment.html", {"form": form})

@login_required
def close_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        offering__facultyassignment__faculty=request.user
    )

    assignment.is_active = False
    assignment.save()

    return redirect("faculty_assignments")

@login_required
def delete_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        offering__facultyassignment__faculty=request.user
    )

    assignment.delete()

    return redirect("faculty_assignments")

@login_required
def download_all_submissions(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        offering__facultyassignment__faculty=request.user
    )

    submissions = AssignmentSubmission.objects.filter(assignment=assignment)

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{assignment.title}.zip"'

    zip_file = zipfile.ZipFile(response, "w")

    for submission in submissions:
        if submission.file:
            zip_file.write(
                submission.file.path,
                os.path.basename(submission.file.path)
            )

    zip_file.close()

    return response