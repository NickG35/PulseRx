from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, LoginForm
from pharmacy.forms import PharmacyProfileForm
from patients.forms import PatientProfileForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

    def redirect_url(self):
        user = self.request.user
        if user.role == 'pharmacy':
            return reverse_lazy('pharmacy_home')
        elif user.role == 'patient':
            return reverse_lazy('patient_home')


def role_picker(request):
    if request.method == "POST":
        role=request.POST.get('role')
        return redirect('register_role', role=role)
    return render(request, 'register.html')
        
    

def register_role(request, role):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)

        if role == 'pharmacy':
            profile_form = PharmacyProfileForm(request.POST)
        elif role == 'patient':
            profile_form = PatientProfileForm(request.POST)
        else:
            profile_form = None

        if user_form.is_valid() and profile_form and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = role
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('pharmacy_home' if role == 'pharmacy' else 'patient_home')

        
    else:
        user_form = UserRegistrationForm(initial={'role': role})
        if role == 'pharmacy':
            profile_form = PharmacyProfileForm()
        elif role == 'patient':
            profile_form = PatientProfileForm()
        else:
            profile_form = None
    

    return render(request, 'register_role.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role
    })


