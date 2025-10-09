from django.shortcuts import render, redirect
from pharmacy.models import Prescription
from .models import PatientProfile, MedicationReminder, ReminderTime
from accounts.models import CustomAccount, Thread, Message, Notifications
from .forms import ReminderForm, PharmacyForm
from datetime import datetime, date, timedelta
from django.http import JsonResponse
from django.utils import timezone
import json
from accounts.tasks import send_reminder
from celery import current_app
from datetime import datetime, date
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse

def patient_home(request):
    return render(request, 'patient_home.html')

def prescriptions(request):
    patient = PatientProfile.objects.get(user=request.user)
    all_prescriptions = Prescription.objects.filter(patient=patient).all()
    return render(request, 'prescriptions.html', {
        'prescriptions': all_prescriptions,
    })

def my_pharmacy(request):
    patient = PatientProfile.objects.get(user=request.user)
    current_pharmacy = patient.pharmacy

    if request.method == 'POST':
        form = PharmacyForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('my_pharmacy')
    else:
        form = PharmacyForm(instance=patient)

    return render(request, 'my_pharmacy.html', {
        'pharmacy': current_pharmacy,
        'form': form,
    })

def account(request):
    return render(request, 'account.html')

def reminders(request):
    patient = PatientProfile.objects.get(user=request.user)

    reminders = MedicationReminder.objects.filter(user=patient,is_archived=False, is_active=True)
    for reminder in reminders:
        if reminder.days_left() == 0:
            reminder.archive()
            
    all_reminders = MedicationReminder.objects.filter(user=patient, is_archived=False).order_by('-restoration_time').all()
    archived_reminders = MedicationReminder.objects.filter(user=patient, is_archived=True).order_by('-restoration_time').all()

    time_values = [] 
    selected_prescription_id = None

    if request.method == 'POST':
        form = ReminderForm(request.POST, patient=patient)
        selected_prescription_id = request.POST.get('prescription')

        time_values = [
            v for k, v in request.POST.items() if k.startswith("time_")
        ]

        if any(val == "" for val in time_values):
            form.add_error(None, "All time fields must be filled.")

        if form.is_valid():
            reminder = form.save(commit=False)
            day_amount = int(request.POST.get('day_amount'))
            reminder.remaining_days = day_amount
            reminder.user = patient
            reminder.save()

            for time in request.POST:
                if time.startswith('time_'):
                    time_str = request.POST[time]
                    if time_str:
                        time_obj = datetime.strptime(time_str, "%H:%M").time().replace(second=0, microsecond=0)
                        rt = ReminderTime.objects.create(reminder=reminder, time=time_obj)
                        now = timezone.localtime()
                        eta = timezone.make_aware(datetime.combine(date.today(), time_obj))
                        if eta < now:
                            eta += timedelta(days=1)
                        
                        if eta.hour == now.hour and eta.minute == now.minute:
                            eta = now + timedelta(seconds=1)

                        task = send_reminder.apply_async(
                            args=[rt.id],
                            eta=eta
                        )
                        rt.task_id = task.id
                        rt.save(update_fields=["task_id"])

            return redirect('reminders')
    else:
        form = ReminderForm(patient=patient)

    return render(request, 'reminders.html', {
        'form': form,
        'selected_prescription_id': selected_prescription_id,
        "time_values": time_values,
        'all_reminders': all_reminders,
        'archived_reminders': archived_reminders
    })

def reminder_suggestions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prescription_id = data.get('prescription_id')

            results = Prescription.objects.filter(id=prescription_id)
            response_data = [{"quantity": obj.quantity, "dosage": obj.medicine.dosage} for obj in results]

            return JsonResponse({"results": response_data})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def toggle_time(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            time_id = data.get('time_id')
            reminder_time = ReminderTime.objects.get(id=time_id)
            reminder_time.is_active = not reminder_time.is_active
            reminder_time.save()
            return JsonResponse({"success": True})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def toggle_reminder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reminder_id = data.get('reminder_id')
            reminder = MedicationReminder.objects.get(id=reminder_id)

            if reminder.is_active:
                # Turning OFF: Save remaining days before deactivation
                end_date = reminder.start_date + timedelta(days=reminder.day_amount)
                remaining = (end_date - date.today()).days
                reminder.remaining_days = max(0, remaining)
                reminder.times.update(is_active = False)
            else:
                # Turning ON: Reset start_date and clear remaining_days
                reminder.start_date = date.today()
                reminder.remaining_days = None
                reminder.times.update(is_active = True)

                for time_entry in reminder.times.all():
                    time_entry.is_active = True

                    if time_entry.task_id:
                        try:
                            current_app.control.revoke(time_entry.task_id)
                        except Exception:
                            pass

                    now = timezone.localtime()
                    eta = timezone.make_aware(
                        datetime.combine(date.today(), time_entry.time)
                    )
                    if eta < now:
                        eta += timedelta(days=1)
                    
                    if eta.hour == now.hour and eta.minute == now.minute:
                        eta = now + timedelta(seconds=1)
                    
                    task = send_reminder.apply_async(
                        args=[time_entry.id],
                        eta=eta
                    )
                    time_entry.task_id = task.id
                    time_entry.save(update_fields=["is_active", "task_id"])

            reminder.is_active = not reminder.is_active
            reminder.save()
            return JsonResponse({"success": True, "days_left": reminder.days_left()})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def unarchive(request):
        try:
            data = json.loads(request.body)
            reminder_id = data.get('reminder_id')
            reminder = MedicationReminder.objects.get(id=reminder_id)
            reminder.is_active = True
            reminder.is_archived = False
            reminder.times.update(is_active = True)
            reminder.start_date = date.today()
            reminder.remaining_days = reminder.day_amount
            reminder.restoration_time = timezone.now()
            reminder.save()

            for time_entry in reminder.times.all():
                time_entry.is_active = True

                if time_entry.task_id:
                    try:
                        current_app.control.revoke(time_entry.task_id)
                    except Exception:
                        pass
                
                now = timezone.localtime()
                eta = timezone.make_aware(
                    datetime.combine(date.today(), time_entry.time)
                )
                if eta < now:
                    eta += timedelta(days=1)
                
                if eta.hour == now.hour and eta.minute == now.minute:
                    eta = now + timedelta(seconds=1)
                
                task = send_reminder.apply_async(
                    args=[time_entry.id],
                    eta=eta
                )
                time_entry.task_id = task.id
                time_entry.save(update_fields=["is_active", "task_id"])

            patient = PatientProfile.objects.get(user=request.user)
            archive_count = MedicationReminder.objects.filter(user=patient, is_archived=True).count()

            return JsonResponse({"success": True, "day_amount": reminder.day_amount, 'archive_count': archive_count})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def delete_reminder(request):
    try:
        data = json.loads(request.body)
        reminder_id = data.get('reminder_id')
        reminder = MedicationReminder.objects.get(id=reminder_id)
        reminder.delete()
        return JsonResponse({"success": True})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

def edit_reminder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reminder_id = data.get('reminder_id')
            updated_days = data.get('days')
            updated_times = data.get('times', [])

            reminder = MedicationReminder.objects.get(id=reminder_id)
            reminder.remaining_days = updated_days
            reminder.save()


            for time in updated_times:
                time_id = time.get('id')
                new_time = time.get('time')

                try:
                    time_entry = ReminderTime.objects.get(id=time_id, reminder=reminder)
                    parsed_time = datetime.strptime(new_time, "%H:%M").time().replace(second=0, microsecond=0)
                    time_entry.time = parsed_time

                    if time_entry.task_id:
                        try:
                            current_app.control.revoke(time_entry.task_id, terminate=True)
                        except Exception:
                            pass
                    
                    now = timezone.localtime()
                    eta = timezone.make_aware(datetime.combine(date.today(), parsed_time))
                    if eta < now:
                        eta += timedelta(days=1)
                    
                    if eta.hour == now.hour and eta.minute == now.minute:
                        eta = now + timedelta(seconds=1)
                        

                    task = send_reminder.apply_async((time_entry.id,), eta=eta)
                    time_entry.task_id = task.id
                    time_entry.save()


                except ReminderTime.DoesNotExist:
                    continue
            
            time_values = [
                {'id': t.id, 'time': t.time.strftime('%-I:%M %p')}
                for t in reminder.times.all()
            ]

            return JsonResponse({
                "success": True,
                "times": time_values,
                "days": reminder.remaining_days
            })
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def refill(request, prescription_id):
    if request.method == 'POST':
        prescription = Prescription.objects.get(id=prescription_id)

        prescription.refills_left -= 1
        prescription.save()
        
        patient = PatientProfile.objects.get(user=request.user)
        pharmacy = patient.pharmacy
        pharmacists = CustomAccount.objects.filter(pharmacistprofile__pharmacy=pharmacy)
        system_user = CustomAccount.objects.get(role='system')
        users = [system_user] + list(pharmacists) #list of users
        notified_users = list(pharmacists)

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
            content= f"A refill request from {patient.first_name} {patient.last_name} has been sent. ",
            link=reverse('refill_form', args=[prescription.id])
        )

        for u in notified_users:
            Notifications.objects.create(user=u, message=msg)
            
        messages.success(request, "Refill request submitted.")
        
        return redirect('prescriptions')

