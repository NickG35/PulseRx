from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomAccount, Message

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
                'disabled': 'disabled'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'user-info',
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
            'class': 'password-info', 
            'placeholder': 'Current password',
            'disabled': 'disabled'
        }),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs= {
        'class': 'password-info',
        'placeholder': 'New password',
        'disabled': 'disabled'
    }))
    confirmation = forms.CharField(label='', widget=forms.PasswordInput(attrs= {
        'class': 'password-info',
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
        exclude = ['timestamp','read', 'read_time', 'sender', 'recipient']
        