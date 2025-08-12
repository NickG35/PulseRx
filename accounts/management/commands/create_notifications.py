from django.core.management.base import BaseCommand
from django.utils.timezone import localtime
from patients.models import ReminderTime
from accounts.models import Notifications

class Command(BaseCommand):
    help = 'Create notifications for due medication reminders'

    def handle(self, *args, **kwargs):
        now = localtime()
        now_time = now.time()

        due_reminders = ReminderTime.objects.filter(
            is_active=True,
            time__hour=now_time.hour,
            time__minute=now_time.minute
        )

        created_count = 0

        for reminder_time in due_reminders:
            reminder = reminder_time.reminder
            user = reminder.user.user 

            already_exists = Notifications.objects.filter(
                user=user,
                reminder=reminder,
                time__hour=now_time.hour,
                time__minute=now_time.minute
            ).exists()

            if not already_exists:
                Notifications.objects.create(
                    user=user,
                    reminder=reminder
                )
                created_count += 1

        self.stdout.write(f'Created {created_count} new notifications.')