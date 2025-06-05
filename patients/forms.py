from django import forms
from .models import PatientProfile
from pharmacy.models import PharmacyProfile

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        exclude = ['user']