# App/asgi.py (reemplaza 'App' con el nombre de tu proyecto)

import os
from django.core.asgi import get_asgi_application

# PASO 1: Establecer la variable de entorno. Esto debe ir primero.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')

# PASO 2: Inicializar la aplicación de Django.
# Esta línea es la que carga la configuración y prepara Django.
# Debe ejecutarse ANTES de importar cualquier cosa que use los modelos de Django (como tus consumers o routing).
django_asgi_app = get_asgi_application()

# PASO 3: Ahora que Django está listo, podemos importar el resto.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import questionnaires.routing # Este import ahora es seguro.

# PASO 4: Definir el router de protocolos.
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            questionnaires.routing.websocket_urlpatterns
        )
    ),
})
