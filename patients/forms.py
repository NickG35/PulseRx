from django import forms
from .models import PatientProfile, MedicationReminder
from pharmacy.models import Prescription

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        exclude = ['user']

class ReminderForm(forms.ModelForm):
    class Meta:
        model = MedicationReminder
        exclude = ['user']
    
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

        if patient:
            self.fields['prescription'].queryset = Prescription.objects.filter(patient=patient)