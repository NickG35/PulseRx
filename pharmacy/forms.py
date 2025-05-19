from django import forms
from .models import PharmacyProfile

class PharmacyProfileForm(forms.ModelForm):
    class Meta:
        model = PharmacyProfile
        fields = ['pharmacy_name', 'address']