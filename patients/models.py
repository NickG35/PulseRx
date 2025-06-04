from django.db import models
from accounts.models import CustomAccount
from pharmacy.models import Drug, PharmacyProfile

class PatientProfile(models.Model):
    first_name = models.CharField(max_length=100, null=False, default='admin')
    last_name = models.CharField(max_length=100, null=False, default='admin')
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, null=False, default='1')

    def __str__(self):
        return f"{self.user}"

class MedicationReminder(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Drug, on_delete=models.PROTECT)
    frequency = models.CharField(max_length=100)
    time = models.TimeField()

class PatientPharmacy(models.Model):
    patient = models.OneToOneField(CustomAccount, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    pharmacy = models.ForeignKey(PharmacyProfile, on_delete=models.SET_NULL, null=True, related_name='patients')

    def __str__(self):
        return f"{self.patient.username} → {self.pharmacy}"
