from django import forms
from .models import PatientProfile, MedicationReminder
from pharmacy.models import PharmacyProfile
from pharmacy.models import Prescription

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        exclude = ['user']

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['pharmacy']

class ReminderForm(forms.ModelForm):
    class Meta:
        model = MedicationReminder
        exclude = ['user']
        widgets = {
            'time': forms.TimeInput(
                attrs={
                    'id': 'timeInput'
                },
                format='%I:%M %p'
            )
        }
    
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

        self.fields['time'].input_formats = ['%I:%M %p']
        if patient:
            self.fields['prescription'].queryset = Prescription.objects.filter(patient=patient)