from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomAccount(AbstractUser):
    ROLE_CHOICES = (
        ('pharmacy admin', 'Pharmacy Admin'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Thread(models.Model):
    participant = models.ManyToManyField(CustomAccount)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def latest_message(self):
        return self.messages.last()

class Message(models.Model):
    sender = models.ForeignKey(CustomAccount, related_name='sent_messages', on_delete=models.PROTECT)
    recipient = models.ForeignKey(CustomAccount, related_name='received_messages', on_delete=models.PROTECT)
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pharmacy_message' 


class Notifications(models.Model):
    user = models.ForeignKey(CustomAccount, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    reminder = models.ForeignKey('patients.MedicationReminder', on_delete=models.CASCADE, related_name='reminders', blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)