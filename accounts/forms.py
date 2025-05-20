from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomAccount

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('pharmacy', 'Pharmacy'),
        ('patient', 'Patient'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomAccount
        fields = ['username', 'email', 'password1', 'password2', 'role']