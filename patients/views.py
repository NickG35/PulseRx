from django.shortcuts import render

def patient_home(request):
    return render(request, 'patient_home.html')

def prescriptions(request):
    return render(request, 'prescriptions.html')

def my_pharmacy(request):
    return render(request, 'my_pharmacy.html')

def account(request):
    return render(request, 'account.html')

def reminders(request):
    return render(request, 'reminders.html')

def messages(request):
    return render(request, 'messages.html')
