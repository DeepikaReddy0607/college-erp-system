from django.contrib import admin
from .models import (
    AttendanceSession,
    AttendanceRecord,
    AttendanceEditLog,
    AttendanceWindowConfig
)
@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        "course_offering",
        "faculty",
        "date",
        "start_time",
        "end_time",
        "status",
    )

    list_filter = (
        "status",
        "date",
        "course_offering",
    )

    search_fields = (
        "course_offering__course__course_code",
        "faculty__username",
    )

    readonly_fields = (
        "created_at",
        "locked_at",
    )
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "session",
        "status",
        "marked_at",
    )

    list_filter = (
        "status",
        "session__course_offering",
    )

    search_fields = (
        "student__username",
        "student__email",
    )

    readonly_fields = ("marked_at",)
@admin.register(AttendanceEditLog)
class AttendanceEditLogAdmin(admin.ModelAdmin):
    list_display = (
        "attendance_record",
        "edited_by",
        "old_status",
        "new_status",
        "edited_at",
    )

    list_filter = ("edited_at",)

    readonly_fields = (
        "attendance_record",
        "edited_by",
        "old_status",
        "new_status",
        "edited_at",
        "reason",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
@admin.register(AttendanceWindowConfig)
class AttendanceWindowConfigAdmin(admin.ModelAdmin):
    list_display = (
        "edit_window_days",
        "active",
        "updated_at",
    )

    list_editable = ("active",)

    def save_model(self, request, obj, form, change):
        if obj.active:
            AttendanceWindowConfig.objects.exclude(pk=obj.pk).update(active=False)
        super().save_model(request, obj, form, change)
