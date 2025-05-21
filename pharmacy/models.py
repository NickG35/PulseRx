from django.db import models
from accounts.models import CustomAccount

class PharmacyProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return f"{self.user}"

class Drug(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    dosage = models.CharField(max_length=100)
    stock = models.IntegerField(default=100)

class Prescription (models.Model):
    patient = models.ForeignKey(CustomAccount, related_name='patient', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'patient'})
    medicine = models.ForeignKey(Drug, related_name='drug', on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    prescribed_by = models.ForeignKey(CustomAccount, related_name='pharmacist', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'pharmacy'})
    prescribed_on = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField()


