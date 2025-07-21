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
    all_reminders = MedicationReminder.objects.filter(user=patient).all()

    if request.method == 'POST':
        form = ReminderForm(request.POST, patient=patient)
        if form.is_valid():
            reminder = form.save(commit=False)
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
            else:
                # Turning ON: Reset start_date and clear remaining_days
                reminder.start_date = date.today()
                reminder.remaining_days = None

            reminder.is_active = not reminder.is_active
            reminder.save()
            return JsonResponse({"success": True, "is_active": reminder.is_active, "remaining_days": reminder.remaining_days})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    