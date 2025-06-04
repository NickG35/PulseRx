from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomAccount(AbstractUser):
    ROLE_CHOICES = (
        ('pharmacy admin', 'Pharmacy Admin'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)