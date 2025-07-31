# questionnaires/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import F 
# Importa tus modelos
from questionnaires.models import Questionnaire, Question, Option, Submission, Answer 

import logging
logger = logging.getLogger(__name__)

class SurveyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"*** DEBUG CONSUMER: [CONNECT START] Para código: {self.scope['url_route']['kwargs']['access_code']} ***")
        print(f"*** DEBUG CONSUMER: [PRINT] Connect START para código: {self.scope['url_route']['kwargs']['access_code']} ***")

        self.access_code = self.scope['url_route']['kwargs']['access_code']
        self.room_group_name = f'survey_{self.access_code}'

        logger.info(f"*** DEBUG CONSUMER: [CONNECT] Intentando unir al grupo: {self.room_group_name} ***")
        print(f"*** DEBUG CONSUMER: [PRINT] Intentando unir al grupo: {self.room_group_name} ***")
        
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"*** DEBUG CONSUMER: [CONNECT] Unido al grupo: {self.room_group_name} ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Unido al grupo: {self.room_group_name} ***")

            await self.accept() # Aceptar la conexión WebSocket
            logger.info(f"*** DEBUG CONSUMER: [CONNECT] Conexión aceptada. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Conexión aceptada. ***")

            # Intentar enviar estadísticas iniciales (podría fallar aquí si la BD falla)
            logger.info(f"*** DEBUG CONSUMER: [CONNECT] Intentando enviar stats iniciales. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Intentando enviar stats iniciales. ***")
            
            # ¡IMPORTANTE! Asegúrate de que SessionMiddlewareStack esté funcionando correctamente en asgi.py
            # para que self.scope['session'] esté disponible y contenga una session_key.
            # Si no hay session_key, esto podría fallar o usar 'anonymous_session'.
            session_key = self.scope.get('session', {}).session_key
            if not session_key:
                logger.warning("*** DEBUG CONSUMER: [CONNECT] No se encontró session_key en el scope del WebSocket. Usando 'anonymous_session'. ***")
                session_key = "anonymous_session" # Fallback si no hay sesión

            self.session_key = session_key # Guardar para uso posterior en save_answer

            await self.send_initial_stats() # Esta función accede a la BD
            logger.info(f"*** DEBUG CONSUMER: [CONNECT] Stats iniciales enviadas. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Stats iniciales enviadas. ***")

        except Exception as e:
            logger.error(f"*** DEBUG CONSUMER: [CONNECT ERROR] Error crítico durante la conexión WebSocket: {e}", exc_info=True)
            print(f"*** DEBUG CONSUMER: [PRINT] ERROR CRÍTICO DURANTE CONEXIÓN: {e} ***")
            await self.close(code=1011) # Cierre anormal por error interno

        logger.info(f"*** DEBUG CONSUMER: [CONNECT END] Finalizando método connect. ***")
        print(f"*** DEBUG CONSUMER: [PRINT] Connect END. ***")


    async def disconnect(self, close_code):
        logger.info(f"*** DEBUG CONSUMER: [DISCONNECT START] Para código: {self.access_code} con código: {close_code} ***")
        print(f"*** DEBUG CONSUMER: [PRINT] Disconnect START para código: {self.access_code} ***")
        
        if hasattr(self, 'room_group_name'): 
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"*** DEBUG CONSUMER: [DISCONNECT] Abandonó el grupo. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Abandonó el grupo. ***")
        
        logger.info(f"*** DEBUG CONSUMER: [DISCONNECT END] Finalizado disconnect. ***")
        print(f"*** DEBUG CONSUMER: [PRINT] Disconnect END. ***")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        question_id = text_data_json.get('question_id')
        option_id = text_data_json.get('option_id')
        access_code = self.access_code 

        if question_id and option_id:
            await self.save_answer_and_broadcast_stats(question_id, option_id, access_code)

    async def survey_stats_update(self, event):
        question_id = event['question_id']
        stats = event['stats']

        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'question_id': question_id,
            'stats': stats
        }))

    @database_sync_to_async
    def get_current_stats_for_question(self, question_id):
        logger.info(f"*** DEBUG CONSUMER: [GET_STATS] Obteniendo stats para pregunta {question_id} ***")
        print(f"*** DEBUG CONSUMER: [PRINT] get_current_stats_for_question START para {question_id} ***")
        options_stats = {}
        try:
            question = Question.objects.get(id=question_id)
            for option in question.options.all():
                # CORRECCIÓN: Usando 'selected_option' como en tu modelo
                count = Answer.objects.filter(selected_option=option, submission__questionnaire__access_code=self.access_code).count()
                options_stats[option.id] = count
            print(f"*** DEBUG CONSUMER: [PRINT] get_current_stats_for_question END, datos: {options_stats} ***")
            return options_stats
        except Question.DoesNotExist:
            logger.warning(f"*** DEBUG CONSUMER: [DB WARNING] Pregunta {question_id} no existe en DB para stats. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Pregunta {question_id} no existe en DB para stats. ***")
            return {}
        except Exception as e:
            logger.error(f"*** DEBUG CONSUMER: [DB ERROR] Error en get_current_stats_for_question: {e}", exc_info=True)
            print(f"*** DEBUG CONSUMER: [PRINT] ERROR EN get_current_stats_for_question: {e} ***")
            return {}


    @database_sync_to_async
    def get_all_initial_stats(self, access_code):
        logger.info(f"*** DEBUG CONSUMER: [GET_STATS] Obteniendo stats iniciales para {access_code} ***")
        print(f"*** DEBUG CONSUMER: [PRINT] get_all_initial_stats START para {access_code} ***")
        stats_data = {}
        try:
            questionnaire = Questionnaire.objects.get(access_code=access_code)
            logger.info(f"*** DEBUG CONSUMER: [GET_STATS] Cuestionario {access_code} encontrado en DB. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Cuestionario {access_code} encontrado en DB. ***")
            
            for question in questionnaire.questions.all():
                options_stats = {}
                for option in question.options.all():
                    # CORRECCIÓN: Usando 'selected_option' como en tu modelo
                    count = Answer.objects.filter(selected_option=option, submission__questionnaire=questionnaire).count()
                    options_stats[option.id] = count
                stats_data[question.id] = options_stats
            logger.info(f"*** DEBUG CONSUMER: [GET_STATS] Stats obtenidas: {stats_data} ***")
            print(f"*** DEBUG CONSUMER: [PRINT] get_all_initial_stats END, datos: {stats_data} ***")
            return stats_data
        except Questionnaire.DoesNotExist:
            logger.warning(f"*** DEBUG CONSUMER: [GET_STATS WARNING] Cuestionario {access_code} NO existe en DB. ***")
            print(f"*** DEBUG CONSUMER: [PRINT] Cuestionario {access_code} NO existe en DB. ***")
            return {}
        except Exception as e:
            logger.error(f"*** DEBUG CONSUMER: [GET_STATS ERROR] Error inesperado en get_all_initial_stats: {e}", exc_info=True)
            print(f"*** DEBUG CONSUMER: [PRINT] ERROR INESPERADO EN get_all_initial_stats: {e} ***")
            return {}


    async def send_initial_stats(self):
        logger.info(f"*** DEBUG CONSUMER: [SEND_STATS] Llamando a get_all_initial_stats. ***")
        initial_stats = await self.get_all_initial_stats(self.access_code)
        
        if initial_stats is not None:
            logger.info(f"*** DEBUG CONSUMER: [SEND_STATS] Enviando stats iniciales: {initial_stats} ***")
            await self.send(text_data=json.dumps({
                'type': 'initial_stats',
                'stats': initial_stats
            }))
        else:
            logger.error(f"*** DEBUG CONSUMER: [SEND_STATS] No se pudieron obtener stats iniciales, no se enviará nada. ***")


    @database_sync_to_async
    def save_answer_and_get_updated_stats(self, question_id, option_id, access_code):
        logger.info(f"*** DEBUG CONSUMER: [SAVE_ANSWER] Guardando respuesta para Q:{question_id} O:{option_id} A:{access_code} ***")
        print(f"*** DEBUG CONSUMER: [PRINT] save_answer_and_get_updated_stats START ***")
        try:
            question = Question.objects.get(id=question_id)
            option = Option.objects.get(id=option_id, question=question)
            questionnaire = Questionnaire.objects.get(access_code=access_code)

            # CORRECCIÓN: Usa 'session_key' de tu modelo Submission y el scope del WebSocket
            # Para public_survey, queremos que una Submission sea única por (cuestionario, sesión_navegador)
            submission, created_submission = Submission.objects.get_or_create(
                questionnaire=questionnaire,
                session_key=self.scope.get('session', {}).session_key or 'anonymous_websocket_session', # Obtiene la session_key del scope
                # Si SessionMiddlewareStack está correctamente configurado, self.scope['session'].session_key será el ID de sesión
                # 'anonymous_websocket_session' es un fallback si no hay sesión
            )
            logger.info(f"*** DEBUG CONSUMER: Submission: {submission.id} (Creada: {created_submission}) ***")

            # Eliminar respuestas anteriores a la misma pregunta por esta Submission
            # Esto es para permitir cambiar de opción en la misma pregunta sin duplicar respuestas
            Answer.objects.filter(submission=submission, question=question).delete()

            # Guardar la nueva respuesta
            # CORRECCIÓN: Usando 'selected_option' como en tu modelo
            Answer.objects.create(
                submission=submission,
                question=question,
                selected_option=option # Usar selected_option
            )
            logger.info(f"*** DEBUG CONSUMER: Respuesta guardada: Q:{question_id} O:{option.id} ***")

            # Obtener y devolver las estadísticas actualizadas para esta pregunta
            options_stats = {}
            for opt in question.options.all():
                # CORRECCIÓN: Usando 'selected_option' como en tu modelo
                count = Answer.objects.filter(selected_option=opt, submission__questionnaire=questionnaire).count()
                options_stats[opt.id] = count
            
            logger.info(f"*** DEBUG CONSUMER: [SAVE_ANSWER] Stats actualizadas para Q:{question_id}: {options_stats} ***")
            print(f"*** DEBUG CONSUMER: [PRINT] save_answer_and_get_updated_stats END, datos: {options_stats} ***")
            return question_id, options_stats
        
        except (Question.DoesNotExist, Option.DoesNotExist, Questionnaire.DoesNotExist) as e:
            logger.error(f"*** DEBUG CONSUMER: [DB ERROR] Error al guardar/obtener respuesta (modelo no encontrado): {e}", exc_info=True)
            print(f"*** DEBUG CONSUMER: [PRINT] ERROR AL GUARDAR RESPUESTA (MODELO NO ENCONTRADO): {e} ***")
            return None, None
        except Exception as e:
            logger.error(f"*** DEBUG CONSUMER: [DB ERROR] Error inesperado en save_answer_and_get_updated_stats: {e}", exc_info=True)
            print(f"*** DEBUG CONSUMER: [PRINT] ERROR INESPERADO AL GUARDAR RESPUESTA: {e} ***")
            return None, None


    async def save_answer_and_broadcast_stats(self, question_id, option_id, access_code):
        updated_question_id, updated_stats = await self.save_answer_and_get_updated_stats(question_id, option_id, access_code)
        
        if updated_question_id is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'survey_stats_update',
                    'question_id': updated_question_id,
                    'stats': updated_stats
                }
            )