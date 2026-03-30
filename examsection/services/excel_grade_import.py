# grades/services/excel_grades_submit.py

import openpyxl

from django.db import transaction

from accounts.models import StudentProfile

from academics.models import Course
from grades.models import FinalGrade

from grades.utils.grade_validations import (
    validate_grade,
    validate_roll_number,
    validate_course_code
)


def process_grade_excel(file, semester, uploaded_by):

    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    errors = []
    grade_objects = []

    seen_records = set()

    for row_index, row in enumerate(
        sheet.iter_rows(min_row=2, values_only=True), start=2
    ):

        roll_no, student_name, course_code, course_name, grade = row

        # ----------------------------
        # Roll number validation
        # ----------------------------

        if not validate_roll_number(roll_no):
            errors.append(f"Row {row_index}: Invalid roll number")
            continue

        # ----------------------------
        # Course code validation
        # ----------------------------

        if not validate_course_code(course_code):
            errors.append(f"Row {row_index}: Invalid course code")
            continue

        # ----------------------------
        # Grade validation
        # ----------------------------

        if not validate_grade(grade):
            errors.append(f"Row {row_index}: Invalid grade '{grade}'")
            continue

        roll_no = str(roll_no).strip()
        course_code = str(course_code).strip()
        grade = str(grade).strip()

        # ----------------------------
        # Duplicate detection
        # ----------------------------

        record_key = (roll_no, course_code)

        if record_key in seen_records:
            errors.append(
                f"Row {row_index}: Duplicate record for {roll_no} {course_code}"
            )
            continue

        seen_records.add(record_key)

        # ----------------------------
        # Student lookup
        # ----------------------------

        try:
            student = StudentProfile.user.objects.get(roll_no=roll_no)

        except StudentProfile.DoesNotExist:

            errors.append(
                f"Row {row_index}: Student {roll_no} not found"
            )
            continue

        # ----------------------------
        # Course lookup
        # ----------------------------

        try:
            course = Course.objects.get(code=course_code)

        except Course.DoesNotExist:

            errors.append(
                f"Row {row_index}: Course {course_code} not found"
            )
            continue

        # ----------------------------
        # Prevent duplicate grades
        # ----------------------------

        existing = FinalGrade.objects.filter(
            student=student,
            course=course,
            semester=semester
        ).exists()

        if existing:
            errors.append(
                f"Row {row_index}: Grade already exists for {roll_no}"
            )
            continue

        grade_objects.append(
            FinalGrade(
                student=student,
                course=course,
                semester=semester,
                grade=grade,
                uploaded_by=uploaded_by,
                status="draft"
            )
        )

    # ----------------------------
    # Stop if errors exist
    # ----------------------------

    if errors:
        return {
            "success": False,
            "errors": errors
        }

    # ----------------------------
    # Safe database transaction
    # ----------------------------

    with transaction.atomic():

        FinalGrade.objects.bulk_create(grade_objects)

    return {
        "success": True,
        "records_inserted": len(grade_objects)
    }