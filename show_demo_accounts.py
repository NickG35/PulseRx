#!/usr/bin/env python
"""
Quick script to display demo accounts for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PulseRx.settings')
django.setup()

from accounts.models import CustomAccount
from pharmacy.models import PharmacistProfile
from patients.models import PatientProfile

print("=" * 70)
print("PULSERX DEMO ACCOUNTS")
print("=" * 70)

# Pharmacy Admins
print("\n🏥 PHARMACY ADMINS:")
print("-" * 70)
admins = CustomAccount.objects.filter(role='pharmacy admin')
if admins:
    for admin in admins:
        print(f"   Username: {admin.username}")
        print(f"   Name: {admin.first_name} {admin.last_name}")
        print(f"   Email: {admin.email}")
        print(f"   Password: pharmacist123")
        print()
else:
    print("   No pharmacy admins found")

# Pharmacists
print("\n💊 PHARMACISTS:")
print("-" * 70)
pharmacists = CustomAccount.objects.filter(role='pharmacist')
if pharmacists:
    for pharm in pharmacists:
        profile = PharmacistProfile.objects.filter(user=pharm).first()
        pharmacy_name = profile.pharmacy.pharmacy_name if profile else "N/A"
        print(f"   Username: {pharm.username}")
        print(f"   Name: {pharm.first_name} {pharm.last_name}")
        print(f"   Email: {pharm.email}")
        print(f"   Pharmacy: {pharmacy_name}")
        print(f"   Password: pharmacist123")
        print()
else:
    print("   No pharmacists found")

# Patients
print("\n👤 PATIENTS:")
print("-" * 70)
patients = CustomAccount.objects.filter(role='patient')
if patients:
    for patient in patients[:5]:  # Show first 5
        profile = PatientProfile.objects.filter(user=patient).first()
        pharmacy_name = profile.pharmacy.pharmacy_name if profile and profile.pharmacy else "N/A"
        print(f"   Username: {patient.username}")
        print(f"   Name: {patient.first_name} {patient.last_name}")
        print(f"   Email: {patient.email}")
        print(f"   Pharmacy: {pharmacy_name}")
        print(f"   Password: patient123")
        print()
    if patients.count() > 5:
        print(f"   ... and {patients.count() - 5} more patients")
else:
    print("   No patients found")

print("=" * 70)
print("\n💡 TIP: Use different browser profiles or incognito windows")
print("   to test multiple roles simultaneously!")
print("\n📚 See DEMO-SCENARIOS.md for testing workflows")
print("=" * 70)
