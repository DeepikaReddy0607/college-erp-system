from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from assignments.forms import AssignmentForm
from assignments.models import Assignment, AssignmentSubmission
from accounts.models import FacultyProfile
from academics.models import Course, Enrollment, CourseOffering
from django.utils import timezone
from django.http import HttpResponseForbidden

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
    ).distinct()

    return render(request, "faculty/assignment_list.html", {"assignments": assignments})

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
            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                file=file
            )
            return redirect("student_assignments")

    return render(
        request,
        "student/assignments_submit.html",
        {"assignment": assignment}
    )
