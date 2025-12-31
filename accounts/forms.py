from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomAccount, Message
import re

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomAccount
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget = forms.HiddenInput()
        self.fields['email'].help_text = 'Must be unique'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('Username is required.')

        # Must be at least 3 characters
        if len(username.strip()) < 3:
            raise ValidationError('Username must be at least 3 characters long.')

        # Must be at most 150 characters (Django default)
        if len(username.strip()) > 150:
            raise ValidationError('Username must be at most 150 characters long.')

        # Can only contain letters, numbers, underscores, hyphens, periods
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', username):
            raise ValidationError('Username can only contain letters, numbers, underscores, hyphens, and periods.')

        # Must start with a letter or number
        if not re.match(r'^[a-zA-Z0-9]', username):
            raise ValidationError('Username must start with a letter or number.')

        # Check if username already exists
        if CustomAccount.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')

        return username.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')

        # Basic email format validation (Django's EmailField already does some validation)
        # But we'll add additional checks
        email = email.strip().lower()

        # Must contain @ symbol
        if '@' not in email:
            raise ValidationError('Please enter a valid email address.')

        # Check if email already exists
        if CustomAccount.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')

        return email

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
                'class': 'user-info border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
                'disabled': 'disabled'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'user-info border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
                'disabled': 'disabled'
            })
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].widget.attrs['data-original'] = user.username
            self.fields['email'].widget.attrs['data-original'] = user.email

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if CustomAccount.objects.exclude(id=self.instance.id).filter(username=username).exists():
            self.add_error('username', "This username is already taken.")
        if CustomAccount.objects.exclude(id=self.instance.id).filter(email=email).exists():
            self.add_error('email', "This email is already taken.")

        return cleaned_data 
        

class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-info border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
            'placeholder': 'Current password',
            'disabled': 'disabled'
        }),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs= {
        'class': 'password-info border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
        'placeholder': 'New password',
        'disabled': 'disabled'
    }))
    confirmation = forms.CharField(label='', widget=forms.PasswordInput(attrs= {
        'class': 'password-info border-2 border-pulse-gray-100 rounded w-full p-2 focus:border-black focus:outline-none',
        'id': 'confirmation',
        'style': 'display:none;',
        'placeholder': 'Confirm password',
        'disabled': 'disabled'
    }))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user or not self.user.check_password(current_password):
            self.add_error('current_password', "Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("confirmation")
        current_password = cleaned_data.get("current_password")

        if password and confirmation and password != confirmation:
            self.add_error('confirmation', "Passwords do not match.")
        if password and current_password and password == current_password:
            self.add_error('password', "New password must be different than current.")
        if password:
            validate_password(password)

        return cleaned_data

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        exclude = ['timestamp','sender', 'recipient', 'thread', 'link', 'prescription', 'refill_fulfilled', 'drug', 'resupply_fulfilled']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'textarea w-full border-2 border-pulse-gray-300 rounded-lg p-3 focus:border-pulse-red focus:outline-none',
                'placeholder': 'Type your message..',
                'rows': 3,
            }),
        }
        labels = {
            'content': '',
        }
        