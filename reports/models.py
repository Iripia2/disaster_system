from django.db import models
from django.conf import settings


class DisasterCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-exclamation-triangle')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Disaster Categories'


class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    lga = models.CharField(max_length=100, verbose_name='LGA')
    landmark = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.address}, {self.lga}"


class DisasterReport(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reports',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        DisasterCategory,
        on_delete=models.SET_NULL,
        null=True
    )
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    affected_count = models.PositiveIntegerField(default=0, verbose_name='Number of people affected')
    incident_date = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def get_reporter_name(self):
        if self.reporter:
            return self.reporter.get_full_name() or self.reporter.username
        return 'Anonymous'

    def __str__(self):
        return f"[{self.status.upper()}] {self.title}"

    class Meta:
        ordering = ['-reported_at']

    def get_severity_color(self):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark',
        }
        return colors.get(self.severity, 'secondary')

    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'active': 'danger',
            'resolved': 'success',
        }
        return colors.get(self.status, 'secondary')


class MediaAttachment(models.Model):
    FILE_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    )
    report = models.ForeignKey(
        DisasterReport,
        on_delete=models.CASCADE,
        related_name='media'
    )
    file = models.FileField(upload_to='report_media/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='image')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for Report #{self.report.id}"


class ResponderAssignment(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('on_route', 'On Route'),
        ('on_scene', 'On Scene'),
        ('resolved', 'Resolved'),
    )
    report = models.ForeignKey(
        DisasterReport,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='made_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.responder} → Report #{self.report.id}"


class Comment(models.Model):
    report = models.ForeignKey(
        DisasterReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
    is_official = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.user} on Report #{self.report.id}"

    class Meta:
        ordering = ['commented_at']
