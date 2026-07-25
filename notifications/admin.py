from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'notif_type', 'is_read', 'sent_at']
    list_filter = ['is_read', 'notif_type']
