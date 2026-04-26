from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Profile, ActivationToken, PasswordResetToken, SocialAuth


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    # 🔹 Columns shown in list page
    list_display = (
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = ("email",)
    ordering = ("-date_joined",)

    readonly_fields = ("id", "date_joined", "last_login")

    # 🔹 View/Edit user form
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),

        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        (_("Dates"), {
            "fields": ("last_login", "date_joined")
        }),
    )

    # 🔹 Create user form (IMPORTANT FIX)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone_number")
    search_fields = ("user__email", "first_name", "last_name")
    raw_id_fields = ("user",)

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = "Name"


@admin.register(ActivationToken)
class ActivationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "is_expired")
    readonly_fields = ("token_hash", "created_at")

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.boolean = True


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "used")
    readonly_fields = ("token_hash", "created_at")


@admin.register(SocialAuth)
class SocialAuthAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "provider_user_id", "created_at")
    list_filter = ("provider",)