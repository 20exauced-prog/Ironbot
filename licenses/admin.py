from django.contrib import admin
from .models import License


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'expires_at', 'is_valid')
    search_fields = ('user__username', 'user__email', 'key')
    list_filter = ('expires_at', 'created_at')
    ordering = ('expires_at',)
    autocomplete_fields = ('user',)
