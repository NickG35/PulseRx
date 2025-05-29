from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Drug

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