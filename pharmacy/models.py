from django.db import models
from accounts.models import CustomAccount
import uuid

def generate_join_code():
    return uuid.uuid4().hex[:6].upper()

class PharmacyProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=120)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    join_code = models.CharField(max_length=6, unique=True, default=generate_join_code)

    def __str__(self):
        return f"{self.pharmacy_name}"

class PharmacistProfile(models.Model):
    user = models.OneToOneField(CustomAccount, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(PharmacyProfile, on_delete=models.CASCADE, related_name='pharmacists')
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.pharmacy.pharmacy_name})"

class Drug(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    dosage = models.CharField(max_length=100)
    route = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.brand}"

class Prescription (models.Model):
    patient = models.ForeignKey('patients.PatientProfile', related_name='prescription', on_delete=models.SET_NULL, null=True)
    medicine = models.ForeignKey(Drug, related_name='drug', on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    prescribed_by = models.ForeignKey(PharmacistProfile, related_name='pharmacist', on_delete=models.SET_NULL, null=True)
    prescribed_on = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField()

    def __str__(self):
        return f"{self.medicine.name} ({self.medicine.brand})"


