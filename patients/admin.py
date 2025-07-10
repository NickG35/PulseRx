from django.contrib import admin
from .models import PatientProfile, MedicationReminder

# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(MedicationReminder)
