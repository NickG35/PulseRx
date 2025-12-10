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

    # Override email field to make it unique
    email = models.EmailField(unique=True, blank=False)

class Thread(models.Model):
    participant = models.ManyToManyField(CustomAccount)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def latest_message(self):
         return self.messages.order_by('-timestamp').first()

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
    link = models.CharField(max_length=300, blank=True, null=True)
    prescription = models.ForeignKey('pharmacy.Prescription', null=True, blank=True, on_delete=models.CASCADE)
    refill_fulfilled = models.BooleanField(null=True, blank=True, default=None)
    drug = models.ForeignKey('pharmacy.Drug', null=True, blank=True, on_delete=models.CASCADE)
    resupply_fulfilled = models.BooleanField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'pharmacy_message' 

class ReadStatus(models.Model):
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey('CustomAccount', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('message', 'user')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.message.id} - {'Read' if self.read else 'Unread'}"




class Notifications(models.Model):
    user = models.ForeignKey(CustomAccount, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    reminder = models.ForeignKey('patients.MedicationReminder', on_delete=models.CASCADE, related_name='reminders', blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=300, blank=True, null=True)
    prescription = models.ForeignKey('pharmacy.Prescription', on_delete=models.CASCADE, blank=True, null=True)
    drug = models.ForeignKey('pharmacy.Drug', on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)