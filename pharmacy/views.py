from django.shortcuts import render

# Create your views here.
def pharmacy_home(request):
    return render(request, 'pharmacy_home.html')

def create_prescriptions(request):
    return render(request, 'create_prescriptions.html')

def my_patients(request):
    return render(request, 'my_patients.html')

def account(request):
    return render(request, 'pharmacy_account.html')

def inventory(request):
    return render(request, 'inventory.html')

def pharmacy_messages(request):
    return render(request, 'pharmacy_messages.html')