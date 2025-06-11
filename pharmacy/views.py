from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Drug, PharmacyProfile, PharmacistProfile, Prescription
from .forms import PrescriptionForm
from patients.models import PatientProfile
from django.http import JsonResponse
from django.db.models import Q

# Create your views here.
def pharmacy_home(request):
    pharmacy = PharmacyProfile.objects.get(user=request.user)
    return render(request, 'pharmacy_home.html', {
        'pharmacy': pharmacy,
    })

def pharmacist_home(request):
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    return render(request, 'pharmacist_home.html', {
        'pharmacist': pharmacist,
    })

def create_prescriptions(request):
    form = PrescriptionForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('create_prescriptions')
    
    return render(request, 'create_prescriptions.html', {
        'form': form,
    })

def patient_search(request):
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    pharmacy = pharmacist.pharmacy
    pharmacy_patients = PatientProfile.objects.filter(pharmacy=pharmacy)

    query = request.GET.get('q', '').strip()
    if query:
        name_parts = query.split()
        if len(name_parts) == 2:
            first, last = name_parts
            items = pharmacy_patients.filter(Q(first_name__icontains=first) & Q(last_name__icontains=last))
        else:
            items = pharmacy_patients.filter(Q(first_name__icontains=query)| Q(last_name__icontains=query) | Q(id__icontains=query)).order_by('first_name')[:10]

        results= [{'first_name': item.first_name, 'last_name': item.last_name, 'id': item.id} for item in items]
    else:
        results = []
        
    return JsonResponse(results, safe=False)



def my_patients(request):
    pharmacist =  PharmacistProfile.objects.get(user=request.user)
    pharmacy_profile = pharmacist.pharmacy
    patients = PatientProfile.objects.filter(pharmacy=pharmacy_profile).all()

    return render(request, 'my_patients.html', {
        'patients': patients
    })

def account(request):
    return render(request, 'pharmacy_account.html')

def inventory(request):
    drugs = Drug.objects.all()
    paginator = Paginator(drugs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory.html', {
        'page_obj': page_obj
    })

def drug_detail(request, drug_id):
    drug_info = Drug.objects.filter(id=drug_id).all()
    return render(request, 'drug_detail.html', {
        'drug_info': drug_info
    })


def pharmacy_messages(request):
    return render(request, 'pharmacy_messages.html')