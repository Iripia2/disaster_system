from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('new_report', 'New Report'),
        ('assignment', 'Assignment'),
        ('resolved', 'Resolved'),
        ('update', 'Update'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    report = models.ForeignKey(
        'reports.DisasterReport',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True, blank=True
    )
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='update')
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user} — {self.message[:50]}"

    class Meta:
        ordering = ['-sent_at']
