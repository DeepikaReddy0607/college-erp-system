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
    faculty = FacultyProfile.objects.filter(user=request.user).first()
    if not faculty:
        return redirect("faculty_dashboard")
    
    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)
        form.fields['subject'].queryset = Course.objects.all()
        
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.faculty = faculty
            assignment.save()
            return redirect('faculty_assignments')
    else:
        form = AssignmentForm()
        form.fields['subject'].queryset = Course.objects.all()

    return render(request, "faculty/create_assignment.html",{
        "form": form
    })

@login_required
def faculty_assignments(request):
    faculty = FacultyProfile.objects.get(user=request.user)
    assignments = Assignment.objects.filter(faculty=faculty)
    return render(request, "faculty/assignment_list.html", {
        "assignments": assignments
    })

@login_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        faculty__user=request.user
    )

    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related("student")

    submitted_student_ids = submissions.values_list(
        "student_id", flat=True
    )

    offerings = CourseOffering.objects.filter(
        course=assignment.subject,
        is_active=True
    )

    not_submitted = Enrollment.objects.filter(
        offering__in=offerings,
        is_active=True
    ).exclude(
        student_id__in=submitted_student_ids
    ).select_related("student")

    total_students = Enrollment.objects.filter(
    offering__course=assignment.subject,
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

    courses = [e.offering.course for e in enrollments]

    assignments = Assignment.objects.filter(
        subject__in=courses,
        is_active=True
    ).select_related("subject", "faculty")

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
