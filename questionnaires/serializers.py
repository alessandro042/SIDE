# questionnaires/serializers.py

from rest_framework import serializers
from .models import Questionnaire, Question, Option

# --- Serializers para el Admin ---

class OptionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']
        read_only_fields = ['id']

class QuestionAdminSerializer(serializers.ModelSerializer):
    options = OptionAdminSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']
        read_only_fields = ['id']

    # ▼▼▼ VALIDACIÓN AÑADIDA #1 ▼▼▼
    def validate_options(self, value):
        """
        Valida que cada pregunta tenga al menos una opción.
        """
        if not value:
            raise serializers.ValidationError("Cada pregunta debe tener al menos una opción.")
        return value

class QuestionnaireAdminSerializer(serializers.ModelSerializer):
    questions = QuestionAdminSerializer(many=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Questionnaire
        fields = ['id', 'title', 'logo', 'is_active', 'access_code', 'created_by', 'questions']
        read_only_fields = ['id', 'access_code', 'created_by', 'is_active', 'logo']

    # ▼▼▼ VALIDACIÓN AÑADIDA #2 ▼▼▼
    def validate_questions(self, value):
        """
        Valida que el cuestionario tenga al menos una pregunta.
        """
        if not value:
            raise serializers.ValidationError("Un cuestionario debe tener al menos una pregunta.")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        questionnaire = Questionnaire.objects.create(**validated_data)
        for question_data in questions_data:
            options_data = question_data.pop('options')
            question = Question.objects.create(questionnaire=questionnaire, **question_data)
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)
        return questionnaire

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        questions_data = validated_data.get('questions', [])
        existing_questions = {q.id: q for q in instance.questions.all()}
        incoming_question_ids = {q.get('id') for q in questions_data if q.get('id')}
        for q_id, question in existing_questions.items():
            if q_id not in incoming_question_ids:
                question.delete()
        for question_data in questions_data:
            question_id = question_data.get('id', None)
            if question_id:
                question = existing_questions[question_id]
                question.text = question_data.get('text', question.text)
                question.save()
            else:
                question = Question.objects.create(questionnaire=instance, text=question_data['text'])
            options_data = question_data.get('options', [])
            existing_options = {opt.id: opt for opt in question.options.all()}
            incoming_option_ids = {opt.get('id') for opt in options_data if opt.get('id')}
            for opt_id, option in existing_options.items():
                if opt_id not in incoming_option_ids:
                    option.delete()
            for option_data in options_data:
                option_id = option_data.get('id', None)
                if option_id:
                    option = existing_options[option_id]
                    option.text = option_data.get('text', option.text)
                    option.save()
                else:
                    Option.objects.create(question=question, text=option_data['text'])
        return instance


class QuestionnaireListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = ['id', 'title', 'is_active', 'access_code']


# --- Serializers para el Usuario Público (Evaluado) ---

class OptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']

class QuestionPublicSerializer(serializers.ModelSerializer):
    options = OptionPublicSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

class QuestionnairePublicSerializer(serializers.ModelSerializer):
    questions = QuestionPublicSerializer(many=True, read_only=True)
    class Meta:
        model = Questionnaire
        fields = ['id', 'title', 'logo', 'questions']

class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

class SubmissionSerializer(serializers.Serializer):
    answers = AnswerSerializer(many=True)