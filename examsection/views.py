from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from academics.models import CourseOffering
from accounts.utils import is_exam_section, is_faculty
from grades.models import FinalGrade, MarksSubmission

from django.db.models import Count, Q
from django.http import HttpResponse
import openpyxl
from collections import defaultdict

@login_required
def exam_dashboard(request):

    if not is_exam_section(request.user):
        return HttpResponseForbidden()

    offerings = CourseOffering.objects.select_related("course", "semester")

    year_map = {
        1: [],
        2: [],
        3: [],
        4: []
    }

    for offering in offerings:

        sem_number = offering.semester.semester
        year = (sem_number + 1) // 2   # 1→Year1, 3→Year2 etc.

        submissions = MarksSubmission.objects.filter(course_offering=offering)
        grades = FinalGrade.objects.filter(course_offering=offering)

        total_students = submissions.count()
        locked = submissions.filter(is_locked=True).count()

        grades_uploaded = grades.count()
        frozen = grades.filter(is_frozen=True).count()

        ready = (
            total_students > 0 and
            locked == total_students and
            grades_uploaded == total_students and
            frozen == total_students
        )

        year_map[year].append({
            "offering": offering,
            "total_students": total_students,
            "ready": ready
        })

    return render(request, "exam/dashboard.html", {
        "year_map": year_map
    })
@login_required
def download_marks(request, offering_id):

    if not is_exam_section(request.user):
        return HttpResponseForbidden()

    offering = get_object_or_404(CourseOffering, id=offering_id)

    submissions = MarksSubmission.objects.filter(
        course_offering=offering
    ).select_related("student")
    if not submissions.exists():
        return HttpResponse("No marks uploaded yet")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Marks"

    # Header
    ws.append(["Roll No", "Name", "Minor1", "Minor2", "Mid", "End"])

    # Data
    for s in submissions:
        ws.append([
            s.student.username,
            s.student.get_full_name() or "",
            s.minor1,
            s.minor2,
            s.mid,
            s.end
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="marks_{offering.id}.xlsx"'

    wb.save(response)
    return response