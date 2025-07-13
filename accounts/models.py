from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomAccount(AbstractUser):
    ROLE_CHOICES = (
        ('pharmacy admin', 'Pharmacy Admin'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Notifications(models.Model):
    user = models.ForeignKey(CustomAccount, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(CustomAccount, related_name='sent_messages', on_delete=models.PROTECT)
    recipient = models.ForeignKey(CustomAccount, related_name='received_messages', on_delete=models.PROTECT)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_time = models.DateField(null=True)

    class Meta:
        db_table = 'pharmacy_message' 