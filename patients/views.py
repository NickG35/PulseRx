from django.shortcuts import render

def patient_home(request):
    return render(request, 'patient_home.html')
