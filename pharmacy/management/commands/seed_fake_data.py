from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pharmacy.models import PharmacyProfile, PharmacistProfile, generate_join_code
from patients.models import PatientProfile
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Seeds pharmacists and patients with accurate gender and realistic usernames/emails'

    def handle(self, *args, **kwargs):
        fake = Faker()
        fake.unique.clear()
        User = get_user_model()

        pharmacies = PharmacyProfile.objects.all()

        if not pharmacies:
            self.stdout.write(self.style.ERROR("No pharmacies found. Please seed pharmacies first."))
            return

        for pharmacy in pharmacies:
            # Create Pharmacists
            for _ in range(3):
                gender = random.choice(['M', 'F'])
                if gender == 'M':
                    first_name = fake.first_name_male()
                else:
                    first_name = fake.first_name_female()
                last_name = fake.last_name()

                base_username = f"{first_name[0].lower()}{last_name.lower()}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                email = f"{username}@mail.com"
                pharmacist_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='pharmacist123',
                    first_name=first_name,
                    last_name=last_name,
                    role='pharmacist'
                )
                PharmacistProfile.objects.create(
                    user=pharmacist_user,
                    pharmacy=pharmacy,
                    first_name=first_name,
                    last_name=last_name
                )

            # Create Patients
            for _ in range(20):
                gender = random.choice(['M', 'F'])
                if gender == 'M':
                    first_name = fake.first_name_male()
                else:
                    first_name = fake.first_name_female()
                last_name = fake.last_name()

                base_username = f"{first_name[0].lower()}{last_name.lower()}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                email = f"{username}@mail.com"
                phone = fake.numerify(text="###-###-####")

                patient_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='patient123',
                    first_name=first_name,
                    last_name=last_name,
                    role='patient'
                )
                PatientProfile.objects.create(
                    user=patient_user,
                    first_name=first_name,
                    last_name=last_name,
                    dob=fake.date_of_birth(minimum_age=18, maximum_age=90),
                    gender=gender,
                    phone_number=phone,
                    pharmacy=pharmacy
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded pharmacists and patients with gender-matched names."))


