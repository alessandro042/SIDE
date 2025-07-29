# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
# Usamos r'' para que el router no añada otro segmento a la URL.
# Las rutas serán: /api/users/ (listar, crear), /api/users/{id}/ (ver, editar, borrar)
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]