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
                 'class': 'datepicker',
                 'placeholder': 'MM-DD-YYYY'
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


    