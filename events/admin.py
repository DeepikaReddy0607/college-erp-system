from django.contrib import admin
from .models import Event, EventRegistration, EventAttendance, EventCertificate


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'date', 'status', 'total_seats')
    list_filter = ('club', 'status')
    search_fields = ('title',)


admin.site.register(EventRegistration)
admin.site.register(EventAttendance)
admin.site.register(EventCertificate)