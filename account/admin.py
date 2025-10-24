# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User

    # Columns to display in admin list view
    list_display = ["id", "email", "name", "role_display", "is_active", "is_staff", "is_superuser"]
    
    # Filters on right sidebar
    list_filter = ["is_superuser", "is_staff", "is_active", "is_recruiter", "is_seeker"]

    # Field groups when editing user
    fieldsets = [
        ("Credentials", {"fields": ["email", "password"]}),
        ("Personal Info", {"fields": ["name", "city"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser", "is_recruiter", "is_seeker"]}),
    ]

    # Field groups when adding a user
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "password1", "password2", "is_recruiter", "is_seeker"],
            },
        ),
    ]

    search_fields = ["email", "name"]
    ordering = ["email", "id"]

    filter_horizontal = []

    # Custom column to show role nicely
    def role_display(self, obj):
        roles = []
        if obj.is_recruiter:
            roles.append("Recruiter")
        if obj.is_seeker:
            roles.append("Seeker")
        return ", ".join(roles)
    role_display.short_description = "Role"

# Register the custom admin
admin.site.register(User, CustomUserAdmin)
