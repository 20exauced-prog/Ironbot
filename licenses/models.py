from django.db import models
from django.conf import settings
from django.utils import timezone

class License(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.key}"

    @property
    def is_valid(self):
        """Retourne True si la licence n’est pas expirée"""
        return self.expires_at >= timezone.now()