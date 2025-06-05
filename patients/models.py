from django.db import models
from accounts.models import CustomAccount

class PatientProfile(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, null=False)
    pharmacy = models.ForeignKey('pharmacy.PharmacyProfile', on_delete=models.SET_NULL, null=True, related_name='patients')

    def __str__(self):
        return f"{self.user}"

class MedicationReminder(models.Model):
    prescription = models.ForeignKey('pharmacy.Prescription', on_delete=models.CASCADE)
    frequency = models.CharField(max_length=100)
    time = models.TimeField()
