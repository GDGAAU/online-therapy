from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "username", "is_verified",
                    "is_staff", "is_superuser", "date_joined")
    search_fields = ("email", "username")
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username",)}),
        ("Permissions", {"fields": ("is_active", "is_verified",
         "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name",
                    "occupation", "location", "created_at")
    search_fields = ("first_name", "last_name",
                     "user__email", "occupation", "location")
    list_filter = ("created_at",)
    ordering = ("-created_at",)