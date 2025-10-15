from django import forms
from .models import PharmacyProfile, PharmacistProfile, Prescription, Drug
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
        expiration_date = forms.DateField(
            input_formats=['%m-%d-%Y'],
            widget=forms.DateInput(attrs={
                 'class': 'datepicker',
                 'placeholder': 'MM-DD-YYYY'
            })
        )

        class Meta:
            model = Prescription
            exclude = ['prescribed_by', 'refills_left', 'patient', 'medicine']
        
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            for field in self.fields.values():
                field.error_messages = {'required': ''}


    