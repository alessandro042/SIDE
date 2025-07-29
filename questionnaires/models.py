# questionnaires/models.py
from django.db import models
from users.models import User
import uuid

# Manager para el borrado lógico
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Questionnaire(models.Model):
    title = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    access_code = models.CharField(max_length=10, unique=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Borrado Lógico
    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteManager() # Manager por defecto
    all_objects = models.Manager() # Manager para acceder a todos, incluyendo borrados

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = str(uuid.uuid4())[:6].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

# Modelo para registrar quién ha respondido y evitar duplicados
class Submission(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40) # Clave de sesión del navegador
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('questionnaire', 'session_key') # Un usuario (sesión) solo puede responder una vez

class Answer(models.Model):
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)