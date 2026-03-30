# grades/utils/grade_validations.py

ALLOWED_GRADES = ["EX", "A", "B", "C", "D", "P", "M", "F", "X", "R"]


def validate_grade(grade):
    """
    Validate if grade value is allowed.
    """
    if grade is None:
        return False

    grade = str(grade).strip().upper()

    return grade in ALLOWED_GRADES


def validate_roll_number(roll_no):
    """
    Basic roll number validation.
    """
    if not roll_no:
        return False

    roll_no = str(roll_no).strip()

    if not roll_no.isalnum():
        return False
    if len(roll_no) < 6:
        return False

    return True


def validate_course_code(course_code):
    """
    Basic course code validation.
    """
    if not course_code:
        return False

    course_code = str(course_code).strip()

    return True