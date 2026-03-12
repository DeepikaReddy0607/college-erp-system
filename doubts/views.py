from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from notifications.utils import notify
from .models import AnswerUpvote, Doubt, DoubtAnswer
from academics.models import CourseOffering, FacultyAssignment


@login_required
def student_doubts(request):

    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not allowed")

    sp = request.user.studentprofile

    doubts = Doubt.objects.filter(
        offering__department=sp.department,
        offering__year=sp.year,
        offering__section=sp.section
    ).filter(
        Q(doubt_type="SECTION") |
        Q(doubt_type="FACULTY", author=request.user)
    ).select_related("offering").order_by("-created_at")

    return render(
        request,
        "student/doubts_list.html",
        {"doubts": doubts}
    )

@login_required
def ask_doubt(request):

    if not hasattr(request.user, "studentprofile"):
        return HttpResponseForbidden("Not allowed")

    sp = request.user.studentprofile

    offerings = CourseOffering.objects.filter(
        department=sp.department,
        year=sp.year,
        section=sp.section,
        is_active=True
    )

    if request.method == "POST":

        offering = request.POST.get("offering")
        doubt_type = request.POST.get("doubt_type")
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if not all([offering, doubt_type, title, description]):
            return render(
                request,
                "student/ask_doubt.html",
                {"offerings": offerings, "error": "All fields required"}
            )

        Doubt.objects.create(
            author=request.user,
            offering_id=offering,
            doubt_type=doubt_type,
            title=title,
            description=description
        )

        return redirect("student_doubts")

    return render(
        request,
        "student/ask_doubt.html",
        {"offerings": offerings}
    )

@login_required
def doubt_detail(request, doubt_id):

    doubt = get_object_or_404(Doubt, id=doubt_id)
    user = request.user

    # ===== STUDENT =====
    if hasattr(user, "studentprofile"):

        sp = user.studentprofile

        if (
            doubt.offering.department != sp.department or
            doubt.offering.year != sp.year or
            doubt.offering.section != sp.section
        ):
            return HttpResponseForbidden("Not allowed")

        if doubt.doubt_type == "FACULTY" and doubt.author != user:
            return HttpResponseForbidden("Not allowed")

    # ===== FACULTY =====
    elif hasattr(user, "facultyprofile"):

        if not FacultyAssignment.objects.filter(
            faculty=user,
            offering=doubt.offering,
            is_active=True
        ).exists():
            return HttpResponseForbidden("Not allowed")

    else:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":

        if doubt.is_resolved:
            return HttpResponseForbidden("Doubt resolved")

        DoubtAnswer.objects.create(
            doubt=doubt,
            author=user,
            content=request.POST["content"].strip()
        )

        if user != doubt.author:
            notify(
                user=doubt.author,
                message=f"New reply on your doubt: {doubt.title}"
            )

        return redirect("doubt_detail", doubt_id=doubt.id)

    answers = doubt.answers.all().order_by("-is_accepted", "-created_at")

    context = {
        "doubt": doubt,
        "answers": answers
    }

    # Use correct template depending on role
    if hasattr(user, "facultyprofile"):
        template = "faculty/doubt_detail.html"
    else:
        template = "student/doubt_detail.html"

    return render(request, template, context)

@login_required
def accept_answer(request, answer_id):
    answer = get_object_or_404(DoubtAnswer, id=answer_id)
    doubt = answer.doubt

    if doubt.is_resolved:
        return HttpResponseForbidden("Doubt already resolved")

    is_author = doubt.author == request.user
    is_faculty = hasattr(request.user, "facultyprofile")

    if not (is_author or is_faculty):
        return HttpResponseForbidden("Not allowed")

    DoubtAnswer.objects.filter(
        doubt=doubt,
        is_accepted=True
    ).update(is_accepted=False)

    answer.is_accepted = True
    answer.save()

    doubt.is_resolved = True
    doubt.save()

    notify(
        user=answer.author,
        message=f"Your answer was accepted for doubt: {doubt.title}"
    )

    if answer.author != doubt.author:
        notify(
            user=doubt.author,
            message=f"Your doubt has been resolved: {doubt.title}"
        )

    return redirect("doubt_detail", doubt_id=doubt.id)

@login_required
def faculty_doubts(request):

    if not hasattr(request.user, "facultyprofile"):
        return HttpResponseForbidden("Not allowed")

    assignments = FacultyAssignment.objects.filter(
        faculty=request.user,
        is_active=True
    )

    doubts = Doubt.objects.filter(
        offering__in=assignments.values_list("offering", flat=True)
    ).order_by("-created_at")

    return render(
        request,
        "faculty/doubts_list.html",
        {"doubts": doubts}
    )


@login_required
def toggle_upvote(request, answer_id):
    answer = get_object_or_404(DoubtAnswer, id=answer_id)
    doubt = answer.doubt
    user = request.user

    if hasattr(user, "studentprofile"):
        sp = user.studentprofile
        if(
            doubt.offering.department != sp.department or
            doubt.offering.year != sp.year or
            doubt.offering.section != sp.section
        ):
            return HttpResponseForbidden("Not allowed")
        
        if doubt.doubt_type == "FACULTY" and doubt.author != user:
            return HttpResponseForbidden("Not allowed")
    
    elif hasattr(user, "facultyprofile"):
        if not FacultyAssignment.objects.filter(
            faculty = user,
            offering=doubt.offering,
            is_active=True
        ).exists():
            return HttpResponseForbidden("Not allowed")
    
    else:
        return HttpResponseForbidden("Not allowed")
    
    upvote, created = AnswerUpvote.objects.get_or_create(
        answer=answer,
        user=user
    )

    if not created:
        upvote.delete()
    
    return redirect("doubt_detail", doubt_id=doubt.id)