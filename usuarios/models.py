from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"

    base_role = Role.ADMIN
    
    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)
