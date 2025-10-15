from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Drug, PharmacyProfile, PharmacistProfile, Prescription
from accounts.models import CustomAccount
from accounts.models import Message, Thread, Notifications
from .forms import PrescriptionForm
from patients.models import PatientProfile
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib import messages
from django import forms

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
    form = PrescriptionForm(request.POST or None)
    
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    pharmacy = None
    if request.user.role == 'pharmacy admin':
        pharmacy = PharmacyProfile.objects.get(user=request.user)
        pharmacy = pharmacy
    else:
        pharmacy = pharmacist.pharmacy

    pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)

    if request.method == "POST":
        print(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            patient_id = request.POST.get('patient')
            medicine_id = request.POST.get('medicine')
            patient_profile = PatientProfile.objects.get(id=patient_id)
            medicine = Drug.objects.get(id=medicine_id)

            prescription.patient = patient_profile
            prescription.medicine = medicine
            prescription.prescribed_by = pharmacist

            # Check stock first
            if prescription.quantity > medicine.stock:
                form.add_error('quantity', 'Not enough stock available.')
                return render(request, 'create_prescriptions.html', {'form': form})

            # Reduce stock and save
            medicine.stock -= prescription.quantity
            medicine.save()
            prescription.save()

            system_user = CustomAccount.objects.get(role='system')
            users = [system_user, pharmacy.user] + list(pharmacists) #list of users

            thread = (Thread.objects
                    .filter(participant__in=users)
                    .annotate(num_participants=Count('participant'))
                    .filter(num_participants=len(users))
                    .first())
                
            if not thread:
                thread = Thread.objects.create()
                thread.participant.add(*users)

            # Create notifications
            if 1 <= medicine.stock <= 10:
                msg = Message.objects.create(
                    sender=system_user,
                    thread=thread,
                    content=f"{medicine.name} ({medicine.brand}) is running low.",
                    link = reverse('drug_detail', args=[medicine.id])
                )
                for u in users:
                    Notifications.objects.create(user=u, message=msg)

            if medicine.stock == 0:
                msg = Message.objects.create(
                    sender=system_user,
                    thread=thread,
                    content=f"{medicine.name} ({medicine.brand}) is out of stock.",
                    link = reverse('drug_detail', args=[medicine.id])
                )
                for u in users:
                    Notifications.objects.create(user=u, message=msg)

            messages.success(request, "Prescription created successfully.")
            return redirect('create_prescriptions') 
        else:
            messages.error(request, "There was a problem with your submission. Please check the form.")
            print(form.errors)

    return render(request, 'create_prescriptions.html', {'form': form, 'refill_mode': False})

def patient_search(request):
    if request.user.role in ['pharmacist']:
        pharmacist = PharmacistProfile.objects.get(user=request.user)
        pharmacy = pharmacist.pharmacy
    elif request.user.role in ['pharmacy admin']:
        pharmacy = PharmacyProfile.objects.get(user=request.user)

    if pharmacy:
        pharmacy_patients = PatientProfile.objects.filter(pharmacy=pharmacy)
    else:
        pharmacy_patients = PatientProfile.objects.none()

    query = request.GET.get('q', '').strip()
    email_mode = request.GET.get('email', '') == 'yes'

    if query:
        name_parts = query.split()
        if len(name_parts) == 2:
            first, last = name_parts
            items = pharmacy_patients.filter(Q(first_name__icontains=first) & Q(last_name__icontains=last))
        else:
            items = pharmacy_patients.filter(Q(first_name__icontains=query)| Q(last_name__icontains=query) | Q(id__icontains=query)).order_by('first_name')[:10]

        results= [{'first_name': item.first_name, 'last_name': item.last_name, 'id': item.user.id if email_mode else item.id, 'email': item.user.email} for item in items]
    else:
        results = []
        
    return JsonResponse(results, safe=False)

def medicine_search(request):
    drugs = Drug.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        name_parts = query.split()
        if len(name_parts) == 2:
            generic, brand = name_parts
            items = drugs.filter(Q(name__icontains=generic) & Q(brand__icontains=brand))
        else:
            items = drugs.filter(Q(name__icontains=query)| Q(brand__icontains=query) | Q(id__icontains=query)).order_by('name')[:10]

        results= [{'name': item.name, 'brand': item.brand, 'id': item.id} for item in items]
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

def patient_profile(request, patient_id):
    patient = PatientProfile.objects.get(id=patient_id)
    return render(request, 'patient_profile.html', {
        'patient': patient
    })

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

def resupply(request, drug_id):
    pharmacy = PharmacyProfile.objects.get(user=request.user)
    pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)
    system_user = CustomAccount.objects.get(role='system')
    participants = [system_user, request.user] +  list(pharmacists)

    medicine = Drug.objects.get(id=drug_id)

        
    thread = (Thread.objects
                .filter(participant__in=participants)
                .annotate(num_participants=Count('participant'))
                .filter(num_participants=len(participants))
                .first())
            
    if not thread:
        thread = Thread.objects.create()
        thread.participant.add(*participants)

    msg = Message.objects.create(
        sender=system_user,
        thread=thread,
        content=f"{medicine.name} ({medicine.brand}) has been resupplied.",
        link = reverse('drug_detail', args=[drug_id])
    )

    for u in participants:
        Notifications.objects.create(user=u, message=msg)

        medicine.stock = 100
        medicine.save()

    return redirect('inventory')

def contact_admin(request, drug_id):
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    pharmacy = pharmacist.pharmacy
    pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)
    system_user = CustomAccount.objects.get(role='system')
    participants = [system_user, pharmacy.user] +  list(pharmacists)

    medicine = Drug.objects.get(id=drug_id)

        
    thread = (Thread.objects
                .filter(participant__in=participants)
                .annotate(num_participants=Count('participant'))
                .filter(num_participants=len(participants))
                .first())
            
    if not thread:
        thread = Thread.objects.create()
        thread.participant.add(*participants)
    

    msg = Message.objects.create(
            sender=system_user,
            thread=thread,
            content= f"A resupply of {medicine.name} ({medicine.brand}) has been requested due to low inventory. ",
            link = reverse('drug_detail', args=[drug_id])
        )

    for u in participants:
        Notifications.objects.create(user=u, message=msg)


    return redirect('inventory')

def refill_form(request, prescription_id):
    old_prescription = Prescription.objects.get(id=prescription_id)
    patient = old_prescription.patient
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    pharmacy = pharmacist.pharmacy
        
    pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)

    system_user = CustomAccount.objects.get(role='system')

    if request.method == 'POST':

        form = PrescriptionForm(request.POST)
        if form.is_valid():
            new_prescription = form.save(commit=False)
            new_prescription.prescribed_by = pharmacist
            new_prescription.patient = old_prescription.patient
            new_prescription.medicine = old_prescription.medicine
            new_prescription.refill_pending = False
            medicine = new_prescription.medicine

            # Check stock first
            if new_prescription.quantity > medicine.stock:
                form.add_error('quantity', 'Not enough stock available.')
                return render(request, 'create_prescriptions.html', {'form': form})
            
            # Reduce stock and save
            medicine.stock -= new_prescription.quantity
            medicine.save()
            new_prescription.save()

            
            users = [system_user, patient.user] + list(pharmacists) #list of users
            notified_users = [patient.user] + list(pharmacists)

            thread = (Thread.objects
                    .filter(participant__in=users)
                    .annotate(num_participants=Count('participant'))
                    .filter(num_participants=len(users))
                    .first())
                
            if not thread:
                thread = Thread.objects.create()
                thread.participant.add(*users)
            
            msg = Message.objects.create(
                sender=system_user,
                thread=thread,
                content= f"A refill request has been fulfilled and is ready for pick up.",
                link=reverse('patient_profile', args=[patient.id]),
            )

            for u in notified_users:
                Notifications.objects.create(user=u, message=msg)

            messages.success(request, "Refill completed successfully.")
            return redirect('inventory')
    else:
        form = PrescriptionForm(instance=old_prescription)
        form.initial['date'] = ''
    
    return render(request, 'create_prescriptions.html', {
        'form': form,
        'is_refill': True,
        'old_prescription': old_prescription
    })
            



