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
        exclude = ['user', 'start_date','is_active', 'remaining_days', 'restoration_time']
        
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        self.fields['frequency'].widget.attrs.update({'id': 'frequency'})
        if patient:
            self.fields['prescription'].queryset = Prescription.objects.filter(patient=patient)