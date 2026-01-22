from django.contrib import admin
from .models import TimeSlot, TimetableEntry

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time")

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ("offering", "day", "timeslot", "room")
    list_filter = ("day", "offering__department", "offering__year", "offering__section")
