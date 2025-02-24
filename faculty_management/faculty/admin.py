from django.contrib import admin
from .models import FacultyProfile, Schedule, RescheduleRequest


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone_number', 'is_verified')
    search_fields = ('user__username', 'department', 'phone_number')
    list_filter = ('is_verified',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'faculty', 'date', 'start_time', 'end_time')
    search_fields = ('title', 'faculty__username')
    list_filter = ('date', 'faculty')

@admin.register(RescheduleRequest)
class RescheduleRequestAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'requested_by', 'status', 'created_at')
    search_fields = ('schedule__title', 'requested_by__username')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)
