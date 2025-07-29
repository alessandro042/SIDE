# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Vista para la página de inicio de sesión
def login_view(request):
    return render(request, "login.html")

def dashboard_view(request):
    # La vista ahora solo se encarga de mostrar el cascarón del HTML.
    # El JavaScript hará el resto.
    return render(request, "dashboard.html")

def questionnaire_create_view(request):
    return render(request, "questionnaire_form.html")

def questionnaire_stats_view(request, questionnaire_id):
    # Pasamos el ID a la plantilla para que JavaScript pueda hacer la petición a la API
    context = {'questionnaire_id': questionnaire_id}
    return render(request, "questionnaire_stats.html", context)

# Vista para la página pública de un cuestionario
def public_form_view(request, access_code):
    context = {'access_code': access_code}
    return render(request, "public_form.html", context)

def questionnaire_edit_view(request, questionnaire_id):
    return render(request, "questionnaire_edit_form.html", {'questionnaire_id': questionnaire_id})

def user_management_view(request):
    return render(request, "user_management.html")