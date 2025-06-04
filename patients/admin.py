from django.contrib import admin
from .models import PatientProfile, PatientPharmacy

# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(PatientPharmacy)
