from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from pharmacy.forms import PharmacyProfileForm
from patients.forms import PatientProfileForm
from django.contrib.auth import login

# Create your views here.
def login(request):
    return render(request, 'login.html')

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


