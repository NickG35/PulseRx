from django.contrib import admin
from .models import PharmacyProfile, Prescription, Drug

# Register your models here.
admin.site.register(PharmacyProfile)
admin.site.register(Prescription)
admin.site.register(Drug)
