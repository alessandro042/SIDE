# questionnaires/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Count
from .models import Questionnaire, Question, Option, Answer, Submission

class SurveyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.access_code = self.scope['url_route']['kwargs']['access_code']
        self.room_group_name = f'survey_{self.access_code}'

        # ▼▼▼ VERIFICACIÓN AÑADIDA ▼▼▼
        # Verificamos si el cuestionario existe ANTES de hacer cualquier otra cosa.
        questionnaire_exists = await self.check_questionnaire_exists()
        if not questionnaire_exists:
            # Si no existe, rechazamos la conexión y cerramos.
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        initial_stats = await self.get_all_stats()
        await self.send(text_data=json.dumps({
            'type': 'initial_stats',
            'stats': initial_stats
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        question_id = data['question_id']
        option_id = data['option_id']
        
        await self.save_answer(question_id, option_id)
        stats = await self.get_question_stats(question_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'stats_update',
                'question_id': question_id,
                'stats': stats
            }
        )

    async def stats_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'question_id': event['question_id'],
            'stats': event['stats']
        }))

    # --- Funciones de Base de Datos (con manejo de errores) ---

    @sync_to_async
    def check_questionnaire_exists(self):
        # Esta función ahora solo verifica la existencia.
        return Questionnaire.objects.filter(access_code=self.access_code, is_active=True).exists()

    @sync_to_async
    def save_answer(self, question_id, option_id):
        session_key = self.scope['session'].session_key
        if not session_key:
            self.scope['session'].save()
            session_key = self.scope['session'].session_key

        try:
            questionnaire = Questionnaire.objects.get(access_code=self.access_code)
            submission, created = Submission.objects.get_or_create(
                questionnaire=questionnaire,
                session_key=session_key
            )
            Answer.objects.update_or_create(
                submission=submission,
                question_id=question_id,
                defaults={'selected_option_id': option_id}
            )
        except Questionnaire.DoesNotExist:
            # Si el cuestionario no existe, no hacemos nada.
            pass

    @sync_to_async
    def get_question_stats(self, question_id):
        question = Question.objects.get(id=question_id)
        options = question.options.annotate(votes=Count('answer')).values('id', 'votes')
        return {opt['id']: opt['votes'] for opt in options}

    @sync_to_async
    def get_all_stats(self):
        try:
            questionnaire = Questionnaire.objects.get(access_code=self.access_code)
            all_stats = {}
            for question in questionnaire.questions.all():
                options = question.options.annotate(votes=Count('answer')).values('id', 'votes')
                all_stats[question.id] = {opt['id']: opt['votes'] for opt in options}
            return all_stats
        except Questionnaire.DoesNotExist:
            return {}