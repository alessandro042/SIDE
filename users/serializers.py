# users/serializers.py
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User

# Serializer para crear usuarios. La contraseña es obligatoria.
class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'role')

# Serializer para listar y ver detalles de usuarios. No muestra la contraseña.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role')

# Serializer para actualizar usuarios. La contraseña es opcional.
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role')
        # Hacemos que la contraseña no sea obligatoria en la actualización
        extra_kwargs = {'password': {'required': False}}
    
    def update(self, instance, validated_data):
        # Si se incluye una nueva contraseña, la "hasheamos" correctamente
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user