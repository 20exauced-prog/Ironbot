from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class LoginAttempt(models.Model):
    ip_address = models.CharField(max_length=45, unique=True)
    last_username = models.CharField(max_length=150, blank=True)
    failures = models.PositiveIntegerField(default=0)
    first_attempt_at = models.DateTimeField(default=timezone.now)
    last_attempt_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} ({self.failures})"
