# App/asgi.py

import os
from django.core.asgi import get_asgi_application

# 1. Esta línea DEBE ir primero. Le dice a Django dónde están sus ajustes.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')

# 2. Esta línea carga la aplicación de Django y sus ajustes.
django_asgi_app = get_asgi_application()

# 3. AHORA que Django ya está configurado, podemos importar lo de Channels.
from channels.routing import ProtocolTypeRouter, URLRouter
# Importamos el middleware de sesión explícitamente
from channels.sessions import SessionMiddlewareStack
import questionnaires.routing

application = ProtocolTypeRouter({
    # Para peticiones web normales, usamos la app de Django que ya cargamos.
    "http": django_asgi_app,

    # Envolvemos el enrutador de WebSockets con el middleware de sesión
    # Esto asegura que los WebSockets tengan acceso a la misma sesión que el resto de la web
    "websocket": SessionMiddlewareStack(
        URLRouter(
            questionnaires.routing.websocket_urlpatterns
        )
    ),
})