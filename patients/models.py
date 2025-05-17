from django.db import models
from accounts.models import CustomAccount

class PatientProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, blank=True)
    current_medications = models.TextField(blank=True)