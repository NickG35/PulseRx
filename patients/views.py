from django.shortcuts import render, redirect
from pharmacy.models import Prescription
from .models import PatientProfile, MedicationReminder, ReminderTime
from .forms import ReminderForm, PharmacyForm
from datetime import datetime, date, timedelta
from django.http import JsonResponse
import json

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
        form = PharmacyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('my_pharmacy')
    else:
        form = PharmacyForm()

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
            
    all_reminders = MedicationReminder.objects.filter(user=patient, is_archived=False).all()
    archived_reminders = MedicationReminder.objects.filter(user=patient, is_archived=True).all()

    if request.method == 'POST':
        form = ReminderForm(request.POST, patient=patient)
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
                        time_obj = datetime.strptime(time_str, "%I:%M %p").time()
                        ReminderTime.objects.create(reminder=reminder, time=time_obj)

            return redirect('reminders')
    else:
        form = ReminderForm(patient=patient)

    return render(request, 'reminders.html', {
        'form': form,
        'all_reminders': all_reminders,
        'archived_reminders': archived_reminders
    })

def messages(request):
    return render(request, 'messages.html')

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
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

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
            reminder.start_date = date.today()
            reminder.remaining_days = reminder.day_amount
            reminder.save()

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
            updated_times = data.get('times', [])

            reminder = MedicationReminder.objects.get(id=reminder_id)

            for time in updated_times:
                time_id = time.get('id')
                new_time = time.get('time')

                try:
                    time_entry = ReminderTime.objects.get(id=time_id, reminder=reminder)
                    time_entry.time = new_time
                    time_entry.save()
                except ReminderTime.DoesNotExist:
                    continue

            return JsonResponse({"success": True})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)