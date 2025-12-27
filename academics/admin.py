from django.contrib import admin

from django.contrib import admin
from .models import (
    Course,
    AcademicYear,
    Semester,
    CourseOffering,
    FacultyAssignment,
    Enrollment
)

admin.site.register(Course)
admin.site.register(AcademicYear)
admin.site.register(Semester)
admin.site.register(CourseOffering)
admin.site.register(FacultyAssignment)
admin.site.register(Enrollment)
