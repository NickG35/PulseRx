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
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
    pharmacy = PharmacyProfile.objects.get(user=request.user) if request.user.role == 'pharmacy admin' else pharmacist.pharmacy
    pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)

    if request.method == "POST":
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.prescribed_by = pharmacist
            prescription.patient = form.cleaned_data['patient']
            prescription.medicine = form.cleaned_data['medicine']

            medicine = Drug.objects.get(id=prescription.medicine.id)

            if prescription.quantity > medicine.stock:
                form.add_error('quantity', 'Not enough stock available.')
                return render(request, 'create_prescriptions.html', {
                    'form': form
                })
            
            new_stock = medicine.stock - prescription.quantity

            medicine.stock -= prescription.quantity
            medicine.save()
            prescription.save()


            system_user = CustomAccount.objects.get(role='system')
            users = [system_user, pharmacy.user] + list(pharmacists) #list of users
            thread = Thread.objects.create()
            thread.participant.add(*users)
            channel_layer = get_channel_layer()
            
            # Create notifications
            if 1 <= new_stock <= 30:
                msg = Message.objects.create(
                    sender=system_user,
                    thread=thread,
                    content=f"{medicine.name} ({medicine.brand}) is running low.",
                    link = reverse('drug_detail', args=[medicine.id])
                ) 

                for u in [pharmacy.user] + list(pharmacists):
                    notification_obj = Notifications.objects.create(user=u, message=msg)

                    notification_payload = {
                        "type": "send_notification",
                        "notification": {
                            "id": notification_obj.id,
                            "type": "low_stock",
                            "sender": system_user.first_name,
                            "thread_id": thread.id,
                            "message_id": msg.id,
                            "content": msg.content,
                            "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                            "link": msg.link
                        }
                    }

                    if u.id != request.user.id:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{u.id}", notification_payload
                        )

            elif new_stock == 0:
                msg = Message.objects.create(
                    sender=system_user,
                    thread=thread,
                    content=f"{medicine.name} ({medicine.brand}) is out of stock.",
                    link = reverse('drug_detail', args=[medicine.id])
                )

                for u in [pharmacy.user] + list(pharmacists):
                    notification_obj = Notifications.objects.create(user=u, message=msg)

                    notification_payload = {
                        "type": "send_notification",
                        "notification": {
                            "id": notification_obj.id,
                            "type": "out_of_stock",
                            "sender": system_user.first_name,
                            "thread_id": thread.id,
                            "message_id": msg.id,
                            "content": msg.content,
                            "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                            "link": msg.link
                        }
                    }

                    if u.id != request.user.id:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{u.id}", notification_payload
                        )
            
            msg = Message.objects.create(
                sender=system_user,
                thread=thread,
                content= f"You have a new prescription.",
                link=f"{reverse('patient_profile', args=[prescription.patient.id])}#prescription-{prescription.id}"
            )

            notification_obj = Notifications.objects.create(user=prescription.patient.user, message=msg)
            
            notification_payload = {
                "type": "send_notification",
                "notification": {
                    "id": notification_obj.id,
                    "type": "create_prescription",
                    "sender": system_user.first_name,
                    "thread_id": thread.id,
                    "message_id": msg.id,
                    "content": msg.content,
                    "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                    "link": msg.link
                }
            }

            async_to_sync(channel_layer.group_send)(f"user_{prescription.patient.user.id}", notification_payload)

            messages.success(request, "Prescription created successfully.")
            return redirect(
                f"{reverse('patient_profile', args=[prescription.patient.id])}#prescription-{prescription.id}"
            )
        else:
            messages.error(request, "There was a problem with your submission. Please check the form.")
            print(form.errors)

    return render(request, 'create_prescriptions.html', {
        'form': form, 
        'refill_mode': False,
        'previous_patient': request.POST.get('patient'),
        'previous_medicine': request.POST.get('medicine'),
        'previous_patient_name': request.POST.get('patient_name', ''),
        'previous_medicine_name': request.POST.get('medicine_name', '')
    })

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
    participants = [system_user] +  list(pharmacists)

    medicine = Drug.objects.get(id=drug_id)
    medicine.resupply_pending = False
    medicine.stock = 100
    medicine.save()

    thread = Thread.objects.create()
    thread.participant.add(*participants)

    msg = Message.objects.create(
        sender=system_user,
        thread=thread,
        content=f"{medicine.name} ({medicine.brand}) has been resupplied.",
        link = reverse('drug_detail', args=[drug_id])
    )

    last_request_msg = (
        Message.objects
        .filter(drug=medicine, resupply_fulfilled=False)
        .order_by('-timestamp')
        .first()
    )

    if last_request_msg:
        last_request_msg.resupply_fulfilled = True
        last_request_msg.save()

    channel_layer = get_channel_layer()

    for user in list(pharmacists):
        notification_obj = Notifications.objects.create(user=user, message=msg)

        notification_payload = {
            "type": "send_notification",
            "notification": {
                "id": notification_obj.id,
                "type": "resupply",
                "sender": system_user.first_name,
                "thread_id": thread.id,
                "message_id": msg.id,
                "content": msg.content,
                "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                "link": msg.link
            }
        }

        async_to_sync(channel_layer.group_send)(f"user_{user.id}", notification_payload)

    messages.success(request, "Medication inventory successfully resupplied.")
    return redirect(reverse('drug_detail', args=[medicine.id]))

def contact_admin(request, drug_id):
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    pharmacy = pharmacist.pharmacy
    system_user = CustomAccount.objects.get(role='system')
    participants = [system_user, pharmacy.user]

    medicine = Drug.objects.get(id=drug_id)
    medicine.resupply_pending = True
    medicine.save()

    thread = Thread.objects.create()
    thread.participant.add(*participants)
    

    msg = Message.objects.create(
            sender=system_user,
            thread=thread,
            content= f"A resupply of {medicine.name} ({medicine.brand}) has been requested due to low inventory. ",
            link = reverse('drug_detail', args=[drug_id]),
            drug = medicine,
            resupply_fulfilled = False
        )

    timestamp_local = timezone.localtime(msg.timestamp)
    formatted_timestamp = timestamp_local.strftime("%b %d, %I:%M %p")

    notification_obj = Notifications.objects.create(user=pharmacy.user, message=msg)
    
    channel_layer = get_channel_layer()
    notification_payload = {
        "type": "send_notification",
        "notification": {
            "id": notification_obj.id,
            "type": "resupply_request",
            "sender": system_user.first_name,
            "thread_id": thread.id,
            "message_id": msg.id,
            "content": msg.content,
            "timestamp": formatted_timestamp,
            "link": msg.link
        }
    }

    async_to_sync(channel_layer.group_send)(f"user_{pharmacy.user.id}", notification_payload)

    return redirect(reverse('drug_detail', args=[medicine.id]))

def refill_form(request, prescription_id):
    old_prescription = Prescription.objects.get(id=prescription_id)
    patient = old_prescription.patient
    pharmacist = PharmacistProfile.objects.get(user=request.user)
    pharmacy = pharmacist.pharmacy
    pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)
    system_user = CustomAccount.objects.get(role='system')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=old_prescription)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.prescribed_by = pharmacist
            prescription.refill_pending = False
            prescription.refilled_on = timezone.now()

            medicine = prescription.medicine

            # Check stock first
            if prescription.quantity > medicine.stock:
                form.add_error('quantity', 'Not enough stock available.')
                return render(request, 'create_prescriptions.html', {'form': form})
            
            new_stock = medicine.stock - prescription.quantity

            # Reduce stock and save
            medicine.stock -= prescription.quantity
            medicine.save()
            prescription.save()

            
            users = [system_user, patient.user]
            thread = Thread.objects.create()
            thread.participant.add(*users)
            channel_layer = get_channel_layer()

            if 1 <= new_stock <= 30:
                msg = Message.objects.create(
                    sender=system_user,
                    thread=thread,
                    content=f"{medicine.name} ({medicine.brand}) is running low.",
                    link = reverse('drug_detail', args=[medicine.id])
                ) 

                for u in [pharmacy.user] + list(pharmacists):
                    notification_obj = Notifications.objects.create(user=u, message=msg)

                    notification_payload = {
                        "type": "send_notification",
                        "notification": {
                            "id": notification_obj.id,
                            "type": "low_stock",
                            "sender": system_user.first_name,
                            "thread_id": thread.id,
                            "message_id": msg.id,
                            "content": msg.content,
                            "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                            "link": msg.link
                        }
                    }

                    if u.id != request.user.id:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{u.id}", notification_payload
                        )
            
            elif new_stock == 0:
                msg = Message.objects.create(
                    sender=system_user,
                    thread=thread,
                    content=f"{medicine.name} ({medicine.brand}) is out of stock.",
                    link = reverse('drug_detail', args=[medicine.id])
                )

                for u in [pharmacy.user] + list(pharmacists):
                    notification_obj = Notifications.objects.create(user=u, message=msg)

                    notification_payload = {
                        "type": "send_notification",
                        "notification": {
                            "id": notification_obj.id,
                            "type": "out_of_stock",
                            "sender": system_user.first_name,
                            "thread_id": thread.id,
                            "message_id": msg.id,
                            "content": msg.content,
                            "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                            "link": msg.link
                        }
                    }

                    if u.id != request.user.id:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{u.id}", notification_payload
                        )
                    

            
            msg = Message.objects.create(
                sender=system_user,
                thread=thread,
                content= f"A refill request has been fulfilled and is ready for pick up.",
                link=f"{reverse('patient_profile', args=[patient.id])}#prescription-{prescription.id}"
            )

            last_request_msg = (
                Message.objects
                .filter(prescription=old_prescription, refill_fulfilled=False)
                .order_by('-timestamp')
                .first()
            )

            if last_request_msg:
                last_request_msg.refill_fulfilled = True
                last_request_msg.save()

            notification_obj = Notifications.objects.create(user=patient.user, message=msg)
            
            channel_layer = get_channel_layer()
            notification_payload = {
                "type": "send_notification",
                "notification": {
                    "id": notification_obj.id,
                    "type": "refill",
                    "sender": system_user.first_name,
                    "thread_id": thread.id,
                    "message_id": msg.id,
                    "content": msg.content,
                    "timestamp": timezone.localtime(msg.timestamp).strftime("%b %d, %I:%M %p"),
                    "link": msg.link
                }
            }

            async_to_sync(channel_layer.group_send)(f"user_{patient.user.id}", notification_payload)

            return redirect(f"{reverse('patient_profile', args=[patient.id])}#prescription-{prescription.id}")

    else:
        form = PrescriptionForm(instance=old_prescription)
        form.initial['date'] = ''
    
    return render(request, 'create_prescriptions.html', {
        'form': form,
        'is_refill': True,
        'old_prescription': old_prescription
    })
            



