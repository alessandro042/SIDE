# users/views.py
from rest_framework import viewsets
from .models import User
# Importamos el nuevo serializer
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .permissions import IsSuperAdmin

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que los Super Admins puedan ver, crear, actualizar y eliminar otros usuarios.
    """
    queryset = User.objects.all()
    permission_classes = [IsSuperAdmin]

    def get_serializer_class(self):
        # Usamos un serializer diferente para cada acción
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer