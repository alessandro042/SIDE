# questionnaires/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckSubmissionView, QuestionnaireViewSet, PublicQuestionnaireView, SubmissionView

router = DefaultRouter()
# Usamos r'' para que las rutas del admin sean: /api/questionnaires/
router.register(r'', QuestionnaireViewSet, basename='questionnaire-admin')

urlpatterns = [
    # Incluimos las rutas del router para el admin
    path('', include(router.urls)),
    
    # --- Rutas Públicas (estas no cambian) ---
    path('public/forms/<str:access_code>/', PublicQuestionnaireView.as_view(), name='public-questionnaire'),
    path('public/forms/<str:access_code>/submit/', SubmissionView.as_view(), name='public-submission'),
     path('public/check-submission/', CheckSubmissionView.as_view(), name='public-check-submission'),
]