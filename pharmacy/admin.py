from django.contrib import admin
from .models import PharmacyProfile, Prescription

# Register your models here.
admin.site.register(PharmacyProfile)
admin.site.register(Prescription)
