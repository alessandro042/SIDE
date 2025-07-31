# core/views.py
from django.shortcuts import render, redirect
# IMPORTANTE: Añade estas dos líneas para configurar el logger
import logging
logger = logging.getLogger(__name__)

# Vista para la página de inicio de sesión
def login_view(request):
    return render(request, "login.html")

def dashboard_view(request):
    return render(request, "dashboard.html")

def questionnaire_create_view(request):
    return render(request, "questionnaire_form.html")

def questionnaire_stats_view(request, questionnaire_id):
    # Pasamos el ID a la plantilla para que JavaScript pueda hacer la petición a la API
    context = {'questionnaire_id': questionnaire_id}
    return render(request, "questionnaire_stats.html", context)

# Vista para la página pública de un cuestionario
def public_form_view(request, access_code):
    # ¡Aquí estaba el error! La variable 'logger' no estaba definida
    # Vuelve a cambiar esto en public_form_view
    context = {'access_code': access_code}
    return render(request, "public_form.html", context)
    # Cuando esto funcione y veas la página de éxito, puedes volver a cambiar
    # la línea de arriba por la original que renderiza tu template:
    # context = {'access_code': access_code}
    # return render(request, "public_form.html", context)

def questionnaire_edit_view(request, questionnaire_id):
    return render(request, "questionnaire_edit_form.html", {'questionnaire_id': questionnaire_id})

def user_management_view(request):
    return render(request, "user_management.html")