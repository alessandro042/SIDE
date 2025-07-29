# users/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSuperAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol SUPER_ADMIN."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'

class IsOwner(BasePermission):
    """Permite acceso solo al dueño del objeto."""
    def has_object_permission(self, request, view, obj):
        # El objeto debe tener un atributo 'created_by'
        return obj.created_by == request.user