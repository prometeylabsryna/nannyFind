from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.PARENT
            and request.user.status == User.Status.ACTIVE
        )


class IsNanny(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.NANNY
            and request.user.status in (User.Status.ACTIVE, User.Status.PENDING)
        )


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.role == User.Role.ADMIN or user.is_staff or user.is_superuser
        )
