from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

class CustomAccount(AbstractUser):
    ROLE_CHOICES = (
        ('pharmacy', 'Pharmacy'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)