from django import forms
from .models import PharmacyProfile, PharmacistProfile

class PharmacyProfileForm(forms.ModelForm):
    class Meta:
        model = PharmacyProfile
        exclude = ['user','join_code']

class PharmacistProfileForm(forms.ModelForm):
    join_code = forms.CharField(max_length=6, required=True, help_text="Enter your pharmacy's join code")
    class Meta:
        model = PharmacistProfile
        exclude = ['user','pharmacy']