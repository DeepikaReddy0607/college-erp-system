from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from academics.models import CourseOffering
from .models import Exam

@login_required
def student_exam_schedule(request):
    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not allowed")

    sp = request.user.studentprofile

    exams = Exam.objects.filter(
        offering__department=sp.department,
        offering__year=sp.year,
        offering__section=sp.section
    ).select_related(
        "offering__course",
        "exam_type"
    ).order_by("exam_date", "start_time")

    return render(
        request,
        "student/exams/schedule.html",
        {"exams": exams}
    )



@login_required
def student_exam_syllabus(request):
    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not allowed")

    sp = request.user.studentprofile

    exams = Exam.objects.filter(
        offering__department=sp.department,
        offering__year=sp.year,
        offering__section=sp.section
    ).select_related(
        "offering__course",
        "exam_type",
        "syllabus"
    ).order_by("exam_date")

    return render(
        request,
        "student/exams/syllabus.html",
        {"exams": exams}
    )
