from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
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
    username = forms.CharField(widget=forms.PasswordInput)
