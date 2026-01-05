def is_faculty(user):
    return hasattr(user, "facultyprofile")

def is_hod(user):
    return (
        hasattr(user, "facultyprofile")
        and user.facultyprofile.is_hod
    )
