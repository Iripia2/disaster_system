from django.contrib import admin
from .models import DisasterReport, DisasterCategory, Location, MediaAttachment, ResponderAssignment, Comment


@admin.register(DisasterCategory)
class DisasterCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']

@admin.register(DisasterReport)
class DisasterReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'severity', 'status', 'reporter', 'reported_at']
    list_filter = ['status', 'severity', 'category']
    search_fields = ['title', 'description']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['address', 'city', 'lga']

@admin.register(ResponderAssignment)
class ResponderAssignmentAdmin(admin.ModelAdmin):
    list_display = ['report', 'responder', 'status', 'assigned_at']

admin.site.register(MediaAttachment)
admin.site.register(Comment)
