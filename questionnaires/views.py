from django.db.models import Count, Sum
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from django.utils import timezone # <--- AÑADIR ESTA LÍNEA
from datetime import timedelta # <--- AÑADIR ESTA LÍNEA
from django.http import Http404 # <--- AÑADIR ESTA LÍNEA
from django.db.models.functions import TruncDay
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from users.models import User
from .models import Questionnaire, Submission, Question, Option, Answer
from .serializers import (
    QuestionnaireAdminSerializer,
    QuestionnaireListSerializer,
    QuestionnairePublicSerializer,
    SubmissionSerializer
)
from users.permissions import IsOwner

# --- Vistas para el Administrador ---

class QuestionnaireViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que los Admins gestionen SUS PROPIOS cuestionarios.
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Solo mostrar los cuestionarios del usuario logueado que no estén borrados
        return Questionnaire.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionnaireListSerializer
        return QuestionnaireAdminSerializer

    def perform_create(self, serializer):
        # Asignar el cuestionario al usuario que lo crea
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        # Usar borrado lógico en lugar de físico
        instance.is_deleted = True
        instance.is_active = False # Un cuestionario borrado no puede estar activo
        instance.save()
        
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        questionnaire = self.get_object()
        questionnaire.is_active = not questionnaire.is_active
        questionnaire.save()
        return Response({'status': f"Cuestionario {'activado' if questionnaire.is_active else 'desactivado'}"})

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Vista de estadísticas mejorada que incluye opciones con 0 votos.
        """
        questionnaire = self.get_object()

        # 1. Obtenemos todos los votos y los agrupamos por opción
        vote_counts = Option.objects.filter(question__questionnaire=questionnaire)\
            .annotate(votes=Count('answer'))\
            .values('id', 'votes')

        # Creamos un diccionario para buscar los votos de cada opción fácilmente
        votes_map = {item['id']: item['votes'] for item in vote_counts}

        # 2. Obtenemos todas las preguntas y opciones para construir la respuesta
        questions = Question.objects.filter(questionnaire=questionnaire).prefetch_related('options')
        
        stats_data = {}
        for question in questions:
            stats_data[question.id] = {
                'question_text': question.text,
                'options': [
                    {
                        'option_id': option.id,
                        'option_text': option.text,
                        # Usamos el mapa, si no hay votos para una opción, será 0
                        'votes': votes_map.get(option.id, 0)
                    }
                    for option in question.options.all()
                ]
            }
            
        return Response(stats_data)


# --- Vistas para el Usuario Público (Evaluado) ---

class PublicQuestionnaireView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = QuestionnairePublicSerializer
    # Quitamos el filtro de is_active del queryset
    queryset = Questionnaire.objects.filter(is_deleted=False)
    lookup_field = 'access_code'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # Verificamos si está activo aquí
            if not instance.is_active:
                # Si no está activo, devolvemos un error 403 Forbidden con un mensaje claro
                return Response(
                    {"detail": "Esta encuesta ha sido desactivada por el administrador."},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            # Si el código no existe, devolvemos un 404 con un mensaje claro
            return Response(
                {"detail": "No se encontró ninguna encuesta con ese código de acceso."},
                status=status.HTTP_404_NOT_FOUND
            )
        
class SubmissionView(APIView):
    """
    Vista para que un usuario anónimo envíe sus respuestas a un cuestionario.
    """
    permission_classes = [AllowAny]

    def post(self, request, access_code, format=None):
        # 1. Validar que el cuestionario existe y está activo
        try:
            questionnaire = Questionnaire.objects.get(access_code=access_code, is_active=True, is_deleted=False)
        except Questionnaire.DoesNotExist:
            return Response({"error": "Cuestionario no encontrado o inactivo."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Prevenir respuestas duplicadas usando la sesión del navegador
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        if Submission.objects.filter(questionnaire=questionnaire, session_key=session_key).exists():
            return Response({"error": "Ya has respondido a este cuestionario."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Validar y guardar las respuestas
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            answers_data = serializer.validated_data['answers']
            
            # Crear el registro de que este usuario (sesión) ya respondió
            submission = Submission.objects.create(questionnaire=questionnaire, session_key=session_key)

            # Guardar cada respuesta
            for answer_data in answers_data:
                Answer.objects.create(
                    submission=submission,
                    question_id=answer_data['question_id'],
                    selected_option_id=answer_data['option_id']
                )
            return Response({"success": "Respuestas enviadas correctamente."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CheckSubmissionView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        access_code = request.data.get('access_code')
        if not access_code:
            return Response({'error': 'No se proporcionó código de acceso.'}, status=status.HTTP_400_BAD_REQUEST)

        # La sesión es la forma de identificar a un usuario anónimo
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # Verificamos si ya existe una respuesta para esa encuesta y esa sesión
        has_submitted = Submission.objects.filter(
            questionnaire__access_code=access_code,
            session_key=session_key
        ).exists()

        return Response({'has_submitted': has_submitted})
    


# ... (resto de tus vistas como PublicQuestionnaireView, SubmissionView, CheckSubmissionView) ...

class DashboardStatsView(APIView):
    """
    Vista API para obtener estadísticas generales del dashboard.
    Solo accesible por usuarios autenticados.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # 1. Total de Cuestionarios Creados (solo activos, no borrados)
        total_questionnaires = Questionnaire.objects.filter(is_deleted=False).count()

        # 2. Total de Respuestas Recibidas (sumar las de todos los cuestionarios)
        # Asegúrate de que Submission exista y esté relacionado correctamente
        total_submissions = Submission.objects.count()

        # 3. Total de Usuarios Registrados (en tu sistema, asumiendo todos los roles)
        total_users = User.objects.count() # Contar todos los usuarios en el sistema

        # 4. Tendencia de Respuestas Recibidas (ej. últimos 30 días)
        # Puedes ajustar el rango de días según lo necesites
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        # Agrupar respuestas por día y contarlas
        submissions_by_day = Submission.objects.filter(
            created_at__range=[start_date, end_date]
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        # Formatear los datos para Chart.js
        trend_labels = []
        trend_data = []
        current_date = start_date
        while current_date <= end_date:
            # Buscar el conteo para este día, si no existe, es 0
            count_for_day = next((item['count'] for item in submissions_by_day if item['day'].date() == current_date.date()), 0)
            trend_labels.append(current_date.strftime('%d/%b')) # Formato "01/Jul"
            trend_data.append(count_for_day)
            current_date += timedelta(days=1)


        # 5. Distribución de Cuestionarios por Tipo/Título (ej. los 5 más populares por respuestas)
        # Esto asume que el "tipo" se infiere del título o una categoría
        # Contaremos las respuestas por cuestionario y luego tomaremos los N primeros
        questionnaire_responses = Questionnaire.objects.filter(
            is_deleted=False, # Solo cuestionarios no borrados
            is_active=True # Opcional: solo cuestionarios activos
        ).annotate(
            total_responses=Count('submission')
        ).order_by('-total_responses')[:5] # Los 5 con más respuestas

        type_labels = [q.title for q in questionnaire_responses]
        type_data = [q.total_responses for q in questionnaire_responses]


        return Response({
            'total_questionnaires': total_questionnaires,
            'total_submissions': total_submissions,
            'total_users': total_users,
            'submissions_trend': {
                'labels': trend_labels,
                'data': trend_data,
            },
            'questionnaire_type_distribution': {
                'labels': type_labels,
                'data': type_data,
            },
        }, status=status.HTTP_200_OK)