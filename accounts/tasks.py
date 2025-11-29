from celery import shared_task
from accounts.models import Notifications
from accounts.utils import send_notification_with_counts
from patients.models import MedicationReminder, ReminderTime
from django.utils import timezone

@shared_task
def send_reminder(time_id):
    try:
        reminder_time = ReminderTime.objects.get(id=time_id)
        reminder = reminder_time.reminder
    except MedicationReminder.DoesNotExist:
        return

    if reminder.is_active and reminder.days_left() > 0 and reminder_time.is_active:
        # Create notification
        notif = Notifications.objects.create(
            user=reminder.user.user,
            reminder=reminder
        )

        created_time_local = timezone.localtime(notif.time)
        formatted_time = created_time_local.strftime("%b. %-d, %Y, %-I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")

        # Send notification with automatic unread counts
        send_notification_with_counts(
            user=reminder.user.user,
            notification_data={
                "id": notif.id,
                "type": "reminder",
                "reminder_id": reminder.id,
                "reminder": reminder.prescription.medicine.name,
                "is_read": notif.is_read,
                "created_time": formatted_time
            }
        )

