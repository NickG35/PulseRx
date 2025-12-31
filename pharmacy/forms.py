from django import forms
from django.core.exceptions import ValidationError
import re
from .models import PharmacyProfile, PharmacistProfile, Prescription, Drug
from patients.models import PatientProfile

class PharmacyProfileForm(forms.ModelForm):
    class Meta:
        model = PharmacyProfile
        exclude = ['user','join_code']

    def clean_pharmacy_name(self):
        pharmacy_name = self.cleaned_data.get('pharmacy_name')
        if not pharmacy_name:
            raise ValidationError('Pharmacy name is required.')

        # Must be at least 3 characters
        if len(pharmacy_name.strip()) < 3:
            raise ValidationError('Pharmacy name must be at least 3 characters long.')

        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', pharmacy_name):
            raise ValidationError('Pharmacy name must contain at least one letter.')

        return pharmacy_name.strip()

    def clean_street_address(self):
        street_address = self.cleaned_data.get('street_address')
        if not street_address:
            raise ValidationError('Street address is required.')

        # Must be at least 5 characters
        if len(street_address.strip()) < 5:
            raise ValidationError('Street address must be at least 5 characters long.')

        # Must contain at least one number (for street number)
        if not re.search(r'\d', street_address):
            raise ValidationError('Street address must contain a street number.')

        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', street_address):
            raise ValidationError('Street address must contain a street name.')

        return street_address.strip()

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city:
            raise ValidationError('City is required.')

        # Must be at least 2 characters
        if len(city.strip()) < 2:
            raise ValidationError('City name must be at least 2 characters long.')

        # Should only contain letters, spaces, hyphens, and apostrophes
        if not re.match(r'^[a-zA-Z\s\-\']+$', city):
            raise ValidationError('City name can only contain letters, spaces, hyphens, and apostrophes.')

        return city.strip()

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state:
            raise ValidationError('State is required.')

        # Must be at least 2 characters
        if len(state.strip()) < 2:
            raise ValidationError('State must be at least 2 characters long.')

        # Should only contain letters, spaces, and hyphens
        if not re.match(r'^[a-zA-Z\s\-]+$', state):
            raise ValidationError('State can only contain letters, spaces, and hyphens.')

        return state.strip()

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if not zip_code:
            raise ValidationError('ZIP code is required.')

        zip_code = zip_code.strip()

        # US ZIP code format: 5 digits or 5 digits-4 digits
        if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
            raise ValidationError('ZIP code must be in format: 12345 or 12345-6789.')

        return zip_code

class PharmacistProfileForm(forms.ModelForm):
    join_code = forms.CharField(max_length=6, required=True, help_text="Enter your pharmacy's join code")
    class Meta:
        model = PharmacistProfile
        exclude = ['user','pharmacy']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError('First name is required.')

        # Must be at least 2 characters
        if len(first_name.strip()) < 2:
            raise ValidationError('First name must be at least 2 characters long.')

        # Should only contain letters, spaces, hyphens, and apostrophes
        if not re.match(r'^[a-zA-Z\s\-\']+$', first_name):
            raise ValidationError('First name can only contain letters, spaces, hyphens, and apostrophes.')

        return first_name.strip()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError('Last name is required.')

        # Must be at least 2 characters
        if len(last_name.strip()) < 2:
            raise ValidationError('Last name must be at least 2 characters long.')

        # Should only contain letters, spaces, hyphens, and apostrophes
        if not re.match(r'^[a-zA-Z\s\-\']+$', last_name):
            raise ValidationError('Last name can only contain letters, spaces, hyphens, and apostrophes.')

        return last_name.strip()

    def clean_join_code(self):
        join_code = self.cleaned_data.get('join_code')
        try:
            PharmacyProfile.objects.get(join_code=join_code)
        except PharmacyProfile.DoesNotExist:
            raise forms.ValidationError('Invalid join code. Please contact your pharmacy admin.')
        return join_code

class PrescriptionForm(forms.ModelForm):
        patient = forms.CharField(required=False, widget=forms.HiddenInput())
        medicine = forms.CharField(required=False, widget=forms.HiddenInput())
        class Meta:
             model = Prescription
             fields = ['quantity', 'expiration_date', 'patient', 'medicine']
        
        def clean(self):
            cleaned_data = super().clean()
            patient_id = self.data.get('patient')
            medicine_id = self.data.get('medicine')

             # Validate Patient
            if not patient_id:
                self.add_error('patient', 'Please enter a patient.')
            else:
                try:
                    patient = PatientProfile.objects.get(id=patient_id)
                    cleaned_data['patient'] = patient
                except PatientProfile.DoesNotExist:
                    self.add_error('patient', 'Invalid patient selected.')
            
            if not medicine_id:
              self.add_error('medicine', 'Please enter a medication.')
            else:
                try:
                    medicine = Drug.objects.get(id=medicine_id)
                    cleaned_data['medicine'] = medicine
                except Drug.DoesNotExist:
                    self.add_error('medicine', 'Invalid medication selected.')
            
            quantity = cleaned_data.get('quantity')
            medicine = cleaned_data.get('medicine')

            if quantity is not None:
                if quantity < 1:
                    self.add_error('quantity', 'Please enter a valid quantity.')
                elif medicine and quantity > medicine.stock:
                    self.add_error('quantity', 'Not enough stock available.')

            return cleaned_data



        expiration_date = forms.DateField(
            input_formats=['%m-%d-%Y'],
            widget=forms.DateInput(attrs={
                 'class': 'datepicker border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
                 'placeholder': 'MM-DD-YYYY'
            })
        )

        quantity = forms.IntegerField(
            widget=forms.NumberInput(attrs={
                'class': 'border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
                'placeholder': 'Enter quantity'
            })
        )

        patient = forms.CharField(required=False, widget=forms.HiddenInput())
        medicine = forms.CharField(required=False, widget=forms.HiddenInput())


        class Meta:
            model = Prescription
            exclude = ['prescribed_by', 'refills_left', 'refilled_on', 'refill_pending', 'patient', 'medicine']
        
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            for field in self.fields.values():
                field.error_messages = {'required': ''}


    