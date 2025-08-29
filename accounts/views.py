from django.shortcuts import render, redirect
from .models import Message, Notifications, CustomAccount
from .forms import UserRegistrationForm, LoginForm, AccountUpdateForm, PasswordUpdateForm, MessageForm
from pharmacy.forms import PharmacyProfileForm, PharmacistProfileForm
from patients.forms import PatientProfileForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from pharmacy.models import PharmacyProfile
from patients.models import ReminderTime, PatientProfile
from django.http import JsonResponse
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist

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

def account_messages(request):
    pharmacy_email = None
    if request.user.role in ['patient']:
        current_patient = PatientProfile.objects.get(user=request.user)
        pharmacy_email = current_patient.pharmacy.user.email

    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp').all()
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp').all()
    form = MessageForm()
        
    return render(request, 'messages.html', {
        'form': form,
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'pharmacy_email': pharmacy_email
    })

def send_messages(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        
        if request.user.role in ['pharmacist', 'pharmacy admin']:
            recipient_id = request.POST.get('recipient')
            try:
                recipient = CustomAccount.objects.get(id=recipient_id)
            except CustomAccount.DoesNotExist:
                return JsonResponse({"success": False, "error": "Recipient not found"}, status=400)
        else:
            current_patient = PatientProfile.objects.get(user=request.user)
            recipient = current_patient.pharmacy.user

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()

            created_time_local = timezone.localtime(message.timestamp)
            formatted_time = created_time_local.strftime("%b. %-d, %Y, %-I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")

            return JsonResponse({
                "success": True, 
                "id": message.id, 
                "sender": message.sender.username, 
                "recipient": message.recipient.username, 
                "content": message.content, 
                "timestamp": formatted_time, 
                "read": message.read
            })
        
    return JsonResponse({"success": False}, status=400)


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