from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomAccount

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomAccount
        fields = ['username', 'email', 'password1', 'password2', 'role']
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget = forms.HiddenInput()

User = get_user_model()

class LoginForm (AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomAccount
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'user-info',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'user-info',
            })
        }
        

class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-info', 
            'placeholder': 'Current password',
        }),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs= {
            'class': 'password-info',
            'placeholder': 'new password',
        }),
    )
    confirmation = forms.CharField(widget=forms.PasswordInput(attrs= {
            'class': 'password-info',
            'id': 'confirmation',
            'style': 'display:none;',
            'placeholder': 'confirm password',
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("confirmation")
        current_password = cleaned_data.get("current_password")

        if password and confirmation and password != confirmation:
            raise forms.ValidationError("Passwords do not match.")
        if password and current_password and password == current_password:
            raise forms.ValidationError("New password must be different than current.")
        if password:
            validate_password(password)

        return cleaned_data
