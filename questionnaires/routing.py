# questionnaires/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/survey/(?P<access_code>\w+)/$', consumers.SurveyConsumer.as_asgi()),
]