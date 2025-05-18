from django.db import models
from accounts.models import CustomAccount
from pharmacy.models import Drug

class PatientProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, blank=True)

class MedicationReminder(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Drug, on_delete=models.PROTECT)
    frequency = models.CharField(max_length=100)
    time = models.TimeField()

