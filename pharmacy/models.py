from django.db import models
from accounts.models import CustomAccount

class PharmacyProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=255)
    address = models.TextField()