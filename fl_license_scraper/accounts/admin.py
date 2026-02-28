"""Admin configuration for accounts."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username", "email", "first_name", "last_name",
        "role", "city", "county", "is_active",
    ]
    list_filter = BaseUserAdmin.list_filter + ("role",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("role", "phone", "city", "county", "zip_code", "avatar", "email_notifications"),
        }),
    )
