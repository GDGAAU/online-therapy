from rest_framework.permissions import BasePermission


class IsAdminOnly(BasePermission):
    """Allow access only to users who are both staff and superuser."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff and user.is_superuser)


class IsAdminUser(BasePermission):
    """Allow access only to admin users (staff or superuser)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
