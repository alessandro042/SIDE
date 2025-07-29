# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Rutas para las páginas renderizadas con Django
    path('login/', views.login_view, name='login-page'),
    path('dashboard/', views.dashboard_view, name='dashboard-page'),
    path('create-questionnaire/', views.questionnaire_create_view, name='create-questionnaire-page'),
    path('questionnaire/<int:questionnaire_id>/stats/', views.questionnaire_stats_view, name='stats-page'),
    path('form/<str:access_code>/', views.public_form_view, name='public-form-page'),
    path('edit-questionnaire/<int:questionnaire_id>/', views.questionnaire_edit_view, name='edit-questionnaire-page'),
    path('users/', views.user_management_view, name='user-management-page'),
]