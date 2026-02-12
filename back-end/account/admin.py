# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name')  # show all important fields
    list_display_links = ('id', 'user')  # clickable
    search_fields = ('first_name', 'last_name', 'user__email')  # search by name or user's email
    list_filter = ('user__is_active', 'user__is_staff')  # filter by user status
    ordering = ('id',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    search_fields = ('email',)
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
