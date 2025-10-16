from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomAccount(AbstractUser):
    ROLE_CHOICES = (
        ('pharmacy admin', 'Pharmacy Admin'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
        ('system', 'System'),
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
    recipient = models.ForeignKey(
        CustomAccount,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True, 
        blank=True
    )
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_time = models.DateTimeField(null=True, blank=True)
    link = models.CharField(max_length=300, blank=True, null=True)
    prescription = models.ForeignKey('pharmacy.Prescription', null=True, blank=True, on_delete=models.CASCADE)
    refill_fulfilled = models.BooleanField(null=True, blank=True, default=None)
    drug = models.ForeignKey('pharmacy.Drug', null=True, blank=True, on_delete=models.CASCADE)
    resupply_fulfilled = models.BooleanField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'pharmacy_message' 


class Notifications(models.Model):
    user = models.ForeignKey(CustomAccount, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    reminder = models.ForeignKey('patients.MedicationReminder', on_delete=models.CASCADE, related_name='reminders', blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)