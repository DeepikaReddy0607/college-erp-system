from django.contrib import admin
from .models import ExamType, Exam, ExamSyllabus


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "offering",
        "exam_type",
        "exam_date",
        "start_time",
        "end_time",
        "room",
    )
    list_filter = (
        "exam_type",
        "offering__department",
        "offering__year",
        "offering__section",
    )
    search_fields = ("offering__course__course_code",)


@admin.register(ExamSyllabus)
class ExamSyllabusAdmin(admin.ModelAdmin):
    list_display = ("exam",)
