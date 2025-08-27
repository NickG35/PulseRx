from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from accounts.models import Notifications
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
        notif = Notifications.objects.create(
            user=reminder.user.user,
            reminder=reminder
        )

        created_time_local = timezone.localtime(notif.time)
        formatted_time = created_time_local.strftime("%b. %-d, %Y, %-I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")


        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{reminder.user.user.id}",
            {
                "type": "send_notification",
                "notification": {
                    "id": notif.id,
                    "reminder_id": reminder.id,
                    "reminder": reminder.prescription.medicine.name,
                    "is_read": notif.is_read,
                    "created_time": formatted_time
                }
            }
        )

