from django import forms
from .models import PatientProfile, MedicationReminder
from pharmacy.models import PharmacyProfile
from pharmacy.models import Prescription
from datetime import date

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        exclude = ['user']
        widgets = {
            'dob': forms.DateInput(attrs={
                'type': 'date',
                'max': '9999-12-31',  # Prevent future dates in browser
            }),
            'gender': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'pharmacy': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make pharmacy optional
        self.fields['pharmacy'].required = False

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = date.today()
            if dob > today:
                raise forms.ValidationError("Date of birth cannot be in the future.")

            # Calculate age
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            if age < 13:
                raise forms.ValidationError("You must be at least 13 years old to register.")

            if dob.year < 1900:
                raise forms.ValidationError("Please enter a valid date of birth.")

        return dob

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['pharmacy']

class ReminderForm(forms.ModelForm):
    class Meta:
        model = MedicationReminder
        exclude = ['user', 'start_date','is_active', 'remaining_days', 'restoration_time']
    
    def clean_day_amount(self):
        day_amount = self.cleaned_data.get('day_amount')
        if day_amount <= 0:
            raise forms.ValidationError("Day amount must be greater than zero.")
        return day_amount
    
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        self.fields['frequency'].widget.attrs.update({'id': 'frequency'})
        if patient:
            self.fields['prescription'].queryset = Prescription.objects.filter(patient=patient)