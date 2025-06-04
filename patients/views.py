from django.shortcuts import render, redirect
from .forms import PharmacistForm
from .models import PatientPharmacy

def patient_home(request):
    return render(request, 'patient_home.html')

def prescriptions(request):
    return render(request, 'prescriptions.html')

def my_pharmacy(request):
    user = request.user
    patient_profile, _ = PatientPharmacy.objects.get_or_create(patient=user)

    if request.method == 'POST':
        form = PharmacistForm(request.POST)
        if form.is_valid():
            patient_profile.pharmacy = form.cleaned_data['pharmacy']
            patient_profile.save()
            return redirect('my_pharmacy')
        
    form = PharmacistForm()
    return render(request, 'my_pharmacy.html' , {
        'pharmacies': patient_profile.pharmacy,
        'form': form
    })

def account(request):
    return render(request, 'account.html')

def reminders(request):
    return render(request, 'reminders.html')

def messages(request):
    return render(request, 'messages.html')
