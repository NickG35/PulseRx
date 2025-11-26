from django.shortcuts import render, redirect
from .models import Message, Notifications, CustomAccount, Thread, ReadStatus
from .forms import UserRegistrationForm, LoginForm, AccountUpdateForm, PasswordUpdateForm, MessageForm
from pharmacy.forms import PharmacyProfileForm, PharmacistProfileForm
from patients.forms import PatientProfileForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from pharmacy.models import PharmacyProfile, PharmacistProfile
from patients.models import ReminderTime, PatientProfile
from django.http import JsonResponse, HttpResponse
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user
        if user.role == 'pharmacy admin':
            return reverse_lazy('pharmacy_home')
        elif user.role == 'pharmacist':
            return reverse_lazy('pharmacist_home')
        elif user.role == 'patient':
            return reverse_lazy('patient_home')
        
def logout_view(request):
    logout(request)
    return redirect('login')


def role_picker(request):
    if request.method == "POST":
        role=request.POST.get('role')
        return redirect('register_role', role=role)
    return render(request, 'register.html')

@login_required
def role_redirect(request):
    if request.user.role == 'pharmacy admin':
        return redirect('pharmacy_home')
    elif request.user.role == 'patient':
        return redirect('patient_home')
    return redirect('login') 
    

def register_role(request, role):
    profile_form_classes = {
        'pharmacy admin': PharmacyProfileForm,
        'patient': PatientProfileForm,
        'pharmacist': PharmacistProfileForm,
    }

    ProfileForm = profile_form_classes.get(role)

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST) if ProfileForm else None

        if user_form.is_valid() and profile_form and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = role
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if role == 'pharmacist':
                join_code = profile_form.cleaned_data.get('join_code')
                try:
                    pharmacy = PharmacyProfile.objects.get(join_code=join_code)
                    profile.pharmacy = pharmacy
                except PharmacyProfile.DoesNotExist:
                    profile_form.add_error('join_code', 'Invalid join code. Please contact your pharmacy admin.')
                    return render(request, 'register_role.html', {
                        'user_form': user_form,
                        'profile_form': profile_form,
                        'role': role
                    })
            
            profile.save()
            login(request, user)

            if role == 'pharmacy admin':
                return redirect('pharmacy_home')
            elif role == 'patient':
                return redirect('patient_home')
            elif role == 'pharmacist':
                return redirect('pharmacist_home') 


        
    else:
        user_form = UserRegistrationForm(initial={'role': role})
        profile_form = ProfileForm() if ProfileForm else None
        
    

    return render(request, 'register_role.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role
    })

def account_settings(request):
    user = request.user
    account_form = AccountUpdateForm(instance=user, user=request.user)
    password_form = PasswordUpdateForm(user=request.user)

    if request.method == 'POST':
        if request.POST.get('form_type') == 'account':
            account_form = AccountUpdateForm(request.POST, instance=user, user=request.user)
            if account_form.is_valid():
                account_form.save()
                message = "Account info updated."
                return JsonResponse({'success': True, 'message': message})
            else:
                return JsonResponse({'success': False, 'errors': account_form.errors})

        elif request.POST.get('form_type') == 'password':
            password_form = PasswordUpdateForm(request.POST, user=request.user)
            if password_form.is_valid():
                password = password_form.cleaned_data['password']
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                message = "Password updated successfully."
                return JsonResponse({'success': True, 'message': message,})
            else:
                #ensure your still showing the confirmation field if forms not valid
                return JsonResponse({'success': False, 'errors': password_form.errors})

    return render(request, 'account_settings.html', {
        'account_form': account_form,
        'password_form': password_form,
    })

@never_cache
def account_messages(request):
    pharmacy_name = None
    patient = None

    if request.user.role == 'patient':
        patient = PatientProfile.objects.get(user=request.user)
  
    user_threads = (
        Thread.objects.filter(participant=request.user)
        .exclude(participant__role='system')
        .distinct()
        .order_by('-last_updated')
    )

    for thread in user_threads:
        
        thread.other_participants = thread.participant.exclude(id=request.user.id)
        latest = thread.latest_message
        thread.latest_msg = latest

        if latest:
            read_status = ReadStatus.objects.filter(
                message=latest,
                user=request.user
            ).first()

            thread.user_read = read_status.read if read_status else False
            thread.unread_count = ReadStatus.objects.filter(
                message__thread=thread,
                user=request.user,
                read=False
            ).count()
        else:
            thread.user_read = True
            thread.unread_count = 0
            thread.latest_msg = None

    return render(request, 'messages.html', {
        'threads': user_threads,
        'pharmacy_name': pharmacy_name,
        'patient': patient
    })


def message_search(request):
    thread = Thread.objects.filter(participant=request.user).all()
    messages = Message.objects.filter(thread__in=thread).all()

    query = request.GET.get('q', '').strip()

    if query:
        items = messages.filter(content__icontains=query)

        results= [
            {
                'content': item.content, 
                'id': item.id, 
                'thread_id': item.thread.id
            } 
            for item in items
        ]
    else:
        results = []
        
    return JsonResponse(results, safe=False)


def thread_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    messages = thread.messages.all().order_by("timestamp")

    ReadStatus.objects.filter(
        message__thread=thread,
        user=request.user,
        read=False
    ).update(read=True)

    Notifications.objects.filter(
        user=request.user,
        message__thread=thread,
    ).delete()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{request.user.id}",
        {
            "type": "send_notification",
            "notification": {
                "id": 0, 
                "unread_count": Notifications.objects.filter(user=request.user, is_read=False).count(),
                "unread_messages": ReadStatus.objects.filter(user=request.user, read=False).count(),
            },
        }
    )

    read_status = ReadStatus.objects.filter(
        message__in=messages,
        user=request.user
    ).values_list('message_id', 'read')
    read_map = dict(read_status)
    for message in messages:
        message.user_read = read_map.get(message.id, False)

    system_user = thread.participant.all().filter(role='system').first()

    if system_user:
        thread.other_participants = [system_user]
        other_user = system_user
    elif request.user.role in ['pharmacy admin', 'pharmacist']:
        # Show the patient participant
        other_user = thread.participant.filter(role='patient').first()
        thread.other_participants = [other_user] if other_user else []
    elif request.user.role == 'patient':
        # Show the pharmacy admin
        other_user = thread.participant.filter(role='pharmacy admin').first()
        thread.other_participants = [other_user] if other_user else []
    else:
        thread.other_participants = thread.participant.exclude(id=request.user.id)
        other_user = thread.other_participants.first()
        
    form = MessageForm()

    return render(request, 'threads.html', {
        'thread': thread,
        'messages': messages,
        'form': form,
        'other_user': other_user
    })

        
def delete_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            noti_id = data.get('notification_id')

            if not noti_id:
                return JsonResponse({"error": "missing notification id"}, status=400)
            try:
                notification = Notifications.objects.get(id=noti_id)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Notification not found"}, status=404)
            
            notification.delete()
            return JsonResponse({"success": True})
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def patient_thread(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patientID')

        try:
            patient_profile = PatientProfile.objects.get(id=patient_id)
        except PatientProfile.DoesNotExist:
            return HttpResponse(f"Patient with id={patient_id} does not exist")
        
        patient_user = patient_profile.user

        pharmacy = None
        pharmacy_user = None

        if request.user.role == 'pharmacy admin':
            pharmacy_user = request.user
            pharmacy = PharmacyProfile.objects.get(user=request.user)

        elif request.user.role == 'pharmacist':
            pharmacist_profile = PharmacistProfile.objects.get(user=request.user)
            pharmacy = pharmacist_profile.pharmacy
            pharmacy_user = pharmacy.user
        else:
            pharmacy = patient_profile.pharmacy
            pharmacy_user = pharmacy.user
        
        if not patient_user or not pharmacy_user:
            return HttpResponse(f"patient_user={patient_user}, pharmacy_user={pharmacy_user}")



        thread = (
            Thread.objects.filter(participant=pharmacy_user)
            .filter(participant=patient_user)
            .distinct()
            .first()
        )

        if not thread:
            thread = Thread.objects.create()
            thread.participant.add(pharmacy_user, patient_user)
            
            pharmacists = pharmacy.pharmacists.select_related('user').all()
            pharmacist_users = [p.user for p in pharmacists]
            if pharmacist_users:
                thread.participant.add(*pharmacist_users)

        return redirect('threads', thread_id=thread.id)


@csrf_exempt
def read_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            noti_id = data.get('notification_id')
            notification = Notifications.objects.get(id=noti_id)
            notification.is_read = True
            notification.save()
            return JsonResponse({"success": True})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)