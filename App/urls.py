from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Redirige la página raíz (http://.../) a la de login.
    path('', RedirectView.as_view(url='/login/', permanent=True)),

    # Incluye las URLs de las páginas del frontend (login/, dashboard/, etc.)
    path('', include('core.urls')),

    # --- API ---
    # Define las rutas específicas para cada parte de la API, evitando conflictos.
    path('api/users/', include('users.urls')),
    path('api/questionnaires/', include('questionnaires.urls')),

    # --- Autenticación ---
    # Incluye las URLs de Djoser para login, logout, etc.
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    # --- Admin de Django ---
    path('admin/', admin.site.urls),
]

# Configuración para servir archivos multimedia (logos) en modo de desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)