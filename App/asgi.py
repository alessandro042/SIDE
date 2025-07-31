# App/asgi.py (reemplaza 'App' con el nombre de tu proyecto si es diferente)

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.urls import re_path # Importa re_path
import questionnaires.consumers # Importa tu consumers.py directamente

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        URLRouter([
            # ¡RUTA TEMPORAL PARA DEPURACIÓN!
            # Definimos la ruta WebSocket directamente aquí para aislar el problema.
            re_path(r'ws/survey/(?P<access_code>\w+)/$', questionnaires.consumers.SurveyConsumer.as_asgi()),
        ])
    ),
})