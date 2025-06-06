from django import forms
from .models import PharmacyProfile, PharmacistProfile, Prescription
from patients.models import PatientProfile

class PharmacyProfileForm(forms.ModelForm):
    class Meta:
        model = PharmacyProfile
        exclude = ['user','join_code']

class PharmacistProfileForm(forms.ModelForm):
    join_code = forms.CharField(max_length=6, required=True, help_text="Enter your pharmacy's join code")
    class Meta:
        model = PharmacistProfile
        exclude = ['user','pharmacy']

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop('pharmacy', None)
        super().__init__(*args, **kwargs)
        if pharmacy:
            self.fields['patient'].queryset = PatientProfile.objects.filter(pharmacy=pharmacy)
            self.fields['prescribed_by'].queryset = PharmacistProfile.objects.filter(pharmacy=pharmacy)