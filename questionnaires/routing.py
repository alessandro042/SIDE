# questionnaires/routing.py

from django.urls import re_path
from . import consumers

# Define las rutas para las conexiones WebSoscket de esta aplicación
websocket_urlpatterns = [
    # Esta expresión regular captura el 'access_code' de la URL y lo pasa al consumer
    re_path(r'ws/survey/(?P<access_code>\w+)/$', consumers.SurveyConsumer.as_asgi()),
]
