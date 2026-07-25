from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reporter', 'Reporter'),
        ('responder', 'Responder'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reporter')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

    def is_reporter(self):
        return self.role == 'reporter'

    def is_responder(self):
        return self.role == 'responder'
