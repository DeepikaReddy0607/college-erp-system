def is_student(user):
    """
    True if user has an active student profile
    """
    return hasattr(user, "studentprofile")


def is_faculty(user):
    """
    True if user has an active faculty profile
    """
    return hasattr(user, "facultyprofile")


def is_hod(user):
    """
    True if user is faculty AND marked as HOD
    Assumes FacultyProfile has `is_hod` boolean
    """
    if not hasattr(user, "facultyprofile"):
        return False
    return user.facultyprofile.is_hod


def is_exam_section(user):
    """
    Optional.
    Only if you later add ExamSectionProfile.
    For now, exam section is implicit.
    """
    return hasattr(user, "examsectionprofile")
