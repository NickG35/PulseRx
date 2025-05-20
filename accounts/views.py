from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from pharmacy.forms import PharmacyProfileForm
from patients.forms import PatientProfileForm
from django.contrib.auth import login

# Create your views here.
def login(request):
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        role = request.POST.get('role')

        if role == 'pharmacy':
            profile_form = PharmacyProfileForm(request.POST)
        elif role == 'patient':
            profile_form = PatientProfileForm(request.POST)
        else:
            profile_form = None
        
        if profile_form:
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                login(request, user)
                
                if user.role == 'pharmacy':
                    return redirect('pharmacy_home')
                elif user.role == 'patient':
                    return redirect('patient_home')
    else:
        user_form = UserRegistrationForm()
        profile_form = None

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

