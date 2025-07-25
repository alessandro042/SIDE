from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer, CreateUserSerializer

# --- Coloca las clases de permisos aquí ---
class IsSuperAdmin(permissions.BasePermission):
    """Permiso para verificar si el usuario es Super Admin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'

class IsAdminUser(permissions.BasePermission):
    """Permiso para verificar si el usuario es Admin o Super Admin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'SUPER_ADMIN']
# -------------------------------------------


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    Solo los Super Admins pueden listar, crear, actualizar o eliminar otros usuarios.
    """
    queryset = User.objects.all()
    # Ahora las clases de permisos están definidas en este mismo archivo
    permission_classes = [IsSuperAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer
