from django import forms
from .models import PharmacyProfile, PharmacistProfile, Prescription, Drug, Message
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
            exclude = ['prescribed_by']
            widgets = {
              'patient': forms.HiddenInput(attrs={'class': 'hidden-patient'}),
              'medicine': forms.HiddenInput(attrs={'class': 'hidden-medicine'}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
            self.fields['patient'].queryset = PatientProfile.objects.all()
            self.fields['medicine'].queryset = Drug.objects.all()
            
            for field in self.fields.values():
                field.error_messages = {'required': ''}

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(queryset=PatientProfile.objects.none())

    class Meta:
        model = Message
        exclude = ['timestamp','read', 'read_time', 'sender']
        widgets = {
              'recipient': forms.HiddenInput(attrs={'class': 'hidden-patient'}),
            }
    