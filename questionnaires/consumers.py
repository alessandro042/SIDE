import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import F 
from .models import Questionnaire, Question, Option, Submission, Answer 
import logging

logger = logging.getLogger(__name__)

class SurveyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.access_code = self.scope['url_route']['kwargs']['access_code']
        self.room_group_name = f'survey_{self.access_code}'
        
        # Guardamos la session_key para usarla después.
        # Es crucial que AuthMiddlewareStack esté en asgi.py para que esto funcione.
        self.session_key = self.scope.get('session', {}).session_key
        if not self.session_key:
            logger.warning(f"WebSocket para {self.access_code}: No se encontró session_key. Se generará una por el navegador.")
            # Si la sesión no existe, Django la creará la primera vez que se modifique.
            # No es necesario un fallback aquí si el middleware está bien configurado.

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_initial_stats()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'): 
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        question_id = text_data_json.get('question_id')
        option_id = text_data_json.get('option_id')
        access_code = self.access_code 

        if question_id and option_id:
            # ▼▼▼ CORRECCIÓN DEL NOMBRE DE LA FUNCIÓN ▼▼▼
            # El nombre correcto es el que definimos más abajo.
            await self.broadcast_stats_after_save(question_id, option_id, access_code)

    async def survey_stats_update(self, event):
        question_id = event['question_id']
        stats = event['stats']
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'question_id': question_id,
            'stats': stats
        }))

    @database_sync_to_async
    def get_all_initial_stats(self, access_code):
        stats_data = {}
        try:
            questionnaire = Questionnaire.objects.get(access_code=access_code)
            for question in questionnaire.questions.all():
                options_stats = {}
                for option in question.options.all():
                    count = Answer.objects.filter(selected_option=option).count()
                    options_stats[option.id] = count
                stats_data[question.id] = options_stats
            return stats_data
        except Questionnaire.DoesNotExist:
            return {}

    async def send_initial_stats(self):
        initial_stats = await self.get_all_initial_stats(self.access_code)
        if initial_stats:
            await self.send(text_data=json.dumps({
                'type': 'initial_stats',
                'stats': initial_stats
            }))

    @database_sync_to_async
    def save_answer_and_get_stats(self, question_id, option_id, access_code):
        try:
            question = Question.objects.get(id=question_id)
            option = Option.objects.get(id=option_id, question=question)
            questionnaire = question.questionnaire

            # Asegurarse de que la sesión exista antes de usarla
            if not self.session_key:
                # Esto es un fallback, pero el middleware debería prevenirlo
                self.scope['session'].save()
                self.session_key = self.scope['session'].session_key

            # Usamos get_or_create para manejar la creación de la Submission de forma segura
            submission, created = Submission.objects.get_or_create(
                questionnaire=questionnaire,
                session_key=self.session_key
            )

            # Lógica para permitir cambiar de opción:
            # Borra cualquier respuesta anterior para ESTA pregunta y ESTA submission.
            Answer.objects.filter(submission=submission, question=question).delete()
            
            # Guardar la nueva respuesta
            Answer.objects.create(
                submission=submission,
                question=question,
                selected_option=option
            )

            # Obtener y devolver las estadísticas actualizadas para esta pregunta
            options_stats = {}
            for opt in question.options.all():
                count = Answer.objects.filter(selected_option=opt).count()
                options_stats[opt.id] = count
            
            return question_id, options_stats
        
        except Exception as e:
            logger.error(f"Error en save_answer_and_get_stats: {e}", exc_info=True)
            return None, None

    # He renombrado la función para que sea más clara
    async def broadcast_stats_after_save(self, question_id, option_id, access_code):
        updated_question_id, updated_stats = await self.save_answer_and_get_stats(question_id, option_id, access_code)
        
        if updated_question_id is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'survey_stats_update',
                    'question_id': updated_question_id,
                    'stats': updated_stats
                }
            )
