from django.db import models
from accounts.models import CustomAccount
from pharmacy.models import Drug

class PatientProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user}"

class MedicationReminder(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Drug, on_delete=models.PROTECT)
    frequency = models.CharField(max_length=100)
    time = models.TimeField()

class Pharmacist(models.Model):
    pharmacist = models.ForeignKey(CustomAccount, related_name='patients', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'pharmacist'})

