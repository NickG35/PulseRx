from django.shortcuts import render, redirect
from .models import Message, Notifications, CustomAccount, Thread
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
    pharmacist = None

    if request.user.role  ==  'pharmacist':
        pharmacist = PharmacistProfile.objects.get(user=request.user)
        pharmacy = pharmacist.pharmacy.user
        user_threads = Thread.objects.filter(participant=pharmacy).order_by('-last_updated')
    else:
        user_threads = Thread.objects.filter(participant=request.user).order_by('-last_updated')
        if request.user.role == 'patient':
            patient = PatientProfile.objects.get(user=request.user)
            pharmacy_name = patient.pharmacy.pharmacy_name

    for thread in user_threads:
        if request.user.role == 'pharmacist':
            # Determine what to display in header
            patient_user = thread.participant.all().filter(role='patient').first()
            pharmacy_admin = thread.participant.all().filter(role='pharmacy admin').first()

            if patient_user:
                # Thread is with a patient → show patient
                thread.other_participants = [patient_user]
            elif pharmacy_admin:
                # Thread is with pharmacy → show pharmacy
                thread.other_participants = [pharmacy_admin]
            else:
                # Fallback (shouldn’t happen)
                thread.other_participants = []
        else:
            # For patients and pharmacy admins: exclude self
            thread.other_participants = thread.participant.exclude(id=request.user.id)

        
    return render(request, 'messages.html', {
        'threads': user_threads,
        'pharmacy_name': pharmacy_name
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

def send_messages(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)

        thread_id = request.POST.get('thread_id')

        if not thread_id:
             return JsonResponse({"success": False, "error": "Thread ID missing"}, status=400)
        
        thread = get_object_or_404(Thread, id=thread_id)
        
        if request.user.role == 'pharmacist':
            patient_user = thread.participant.filter(role='patient').first()
            pharmacy_admin = thread.participant.filter(role='pharmacy admin').first()
            if patient_user:
                recipient = patient_user
            elif pharmacy_admin:
                recipient = pharmacy_admin
            else:
                return JsonResponse({"success": False, "error": "No recipient found"}, status=400)
        else:
            recipient = thread.participant.exclude(id=request.user.id).first()
            if not recipient:
                return JsonResponse({"success": False, "error": "No recipient found"}, status=400)


        if form.is_valid():
            message = form.save(commit=False)   
            message.sender = request.user
            message.recipient = recipient
            message.thread = thread
            message.save()

            created_time_local = timezone.localtime(message.timestamp)
            formatted_time = created_time_local.strftime("%b. %-d, %Y, %-I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")

            thread.last_updated = timezone.now()
            thread.save(update_fields=["last_updated"])
            return JsonResponse({
                "success": True,
                "id": message.id,
                "content": message.content,
                "timestamp": formatted_time,
                "read": message.read,
            })
        
    return JsonResponse({"success": False}, status=400)


def thread_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    messages = thread.messages.all().order_by("timestamp")

    # Determine who to show in the header
    if request.user.role == 'pharmacist':

        # Try to get a patient participant first
        patient_user = thread.participant.all().filter(role='patient').first()
        pharmacy_admin = thread.participant.all().filter(role='pharmacy admin').first()

        if patient_user:
            # Thread with patient → show patient
            thread.other_participants = [patient_user]
            other_user = patient_user
        elif pharmacy_admin:
            # Thread with pharmacy → show pharmacy
            thread.other_participants = [pharmacy_admin]
            other_user = pharmacy_admin
        else:
            thread.other_participants = []
            other_user = None
    else:
        thread.other_participants = thread.participant.exclude(id=request.user.id)
        other_user = thread.other_participants.first()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.recipient = other_user
            message.save()
            return redirect ('threads', thread_id=thread.id)
    else:
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
        pharmacy_user = None
        if request.user.role in ['pharmacist']:
            pharmacist = PharmacistProfile.objects.get(user=request.user)
            pharmacy_user = pharmacist.pharmacy.user
        elif request.user.role in ['pharmacy admin']:
            pharmacy_user = request.user
        else:
            patient = PatientProfile.objects.get(user=patient_user)
            pharmacy_user = patient.pharmacy.user

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
            thread.participant.add(pharmacy_user)
            thread.participant.add(patient_user)

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