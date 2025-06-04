from django import forms
from .models import PatientProfile
from pharmacy.models import PharmacyProfile

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['dob', 'gender', 'phone_number']

class PharmacistForm(forms.Form):
    pharmacy = forms.ModelChoiceField(
        queryset=PharmacyProfile.objects.all(),
        label="Select a Pharmacy",
        empty_label="Choose a pharmacy",
        required=True
    )