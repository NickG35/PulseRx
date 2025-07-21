from django.db import models
from accounts.models import CustomAccount
from pharmacy.models import PharmacyProfile, Prescription
from datetime import date, timedelta

class PatientProfile(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, null=False)
    pharmacy = models.ForeignKey(PharmacyProfile, on_delete=models.SET_NULL, null=True, related_name='patients')

    def __str__(self):
        return f"{self.user}"

class MedicationReminder(models.Model):
    user = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    frequency = models.PositiveIntegerField(choices=[(i, f"{i}") for i in range(1, 6)])
    start_date = models.DateField(default=date.today)
    day_amount = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    remaining_days = models.PositiveIntegerField(null=True, blank=True)

    def days_left(self):
        if self.is_active:
            total_days = self.remaining_days if self.remaining_days is not None else self.day_amount
            return max(0, (self.start_date + timedelta(days=total_days) - date.today()).days)
        else:
            return self.remaining_days or 0

class ReminderTime(models.Model):
    reminder = models.ForeignKey(MedicationReminder, on_delete=models.CASCADE, related_name='times')
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
