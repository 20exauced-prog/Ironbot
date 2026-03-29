from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, LoginAttempt


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplementaires', {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplementaires', {'fields': ('email', 'phone_number')}),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'last_username', 'failures', 'first_attempt_at', 'last_attempt_at')
    search_fields = ('ip_address', 'last_username')
    readonly_fields = ('ip_address', 'last_username', 'failures', 'first_attempt_at', 'last_attempt_at')

    def has_add_permission(self, request):
        return False
