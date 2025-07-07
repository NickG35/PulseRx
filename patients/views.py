from django.shortcuts import render, redirect
from pharmacy.models import Prescription
from .models import PatientProfile

def patient_home(request):
    return render(request, 'patient_home.html')

def prescriptions(request):
    patient = PatientProfile.objects.get(user=request.user)
    all_prescriptions = Prescription.objects.filter(patient=patient).all()
    return render(request, 'prescriptions.html', {
        'prescriptions': all_prescriptions,
    })

def my_pharmacy(request):
    patient = PatientProfile.objects.get(user=request.user)
    current_pharmacy = patient.pharmacy
    return render(request, 'my_pharmacy.html', {
        'pharmacy': current_pharmacy,
    })

def account(request):
    return render(request, 'account.html')

def reminders(request):
    return render(request, 'reminders.html')

def messages(request):
    return render(request, 'messages.html')
