from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pharmacy.models import PharmacyProfile, PharmacistProfile, Drug, Prescription
from patients.models import PatientProfile, MedicationReminder, ReminderTime
from accounts.models import Thread, Message, ReadStatus, Notifications
from datetime import date, datetime, timedelta, time
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seeds demo scenarios: archived reminders, messages, low/out of stock items, refill requests, etc.'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Get or create demo pharmacy
        pharmacy = PharmacyProfile.objects.first()
        if not pharmacy:
            self.stdout.write(self.style.ERROR("No pharmacy found. Please seed pharmacies first."))
            return

        # Get or create pharmacist
        pharmacist_user = User.objects.filter(role='pharmacist').first()
        if not pharmacist_user:
            pharmacist_user = User.objects.create_user(
                username='drjones',
                email='drjones@mail.com',
                password='pharmacist123',
                first_name='Sarah',
                last_name='Jones',
                role='pharmacist'
            )
            pharmacist = PharmacistProfile.objects.create(
                user=pharmacist_user,
                pharmacy=pharmacy,
                first_name='Sarah',
                last_name='Jones'
            )
        else:
            pharmacist = PharmacistProfile.objects.filter(user=pharmacist_user).first()

        # Get or create patients
        patients = list(PatientProfile.objects.all()[:5])
        if len(patients) < 2:
            self.stdout.write(self.style.ERROR("Need at least 2 patients. Please seed patients first."))
            return

        patient1, patient2 = patients[0], patients[1]
        patient3 = patients[2] if len(patients) > 2 else patient1

        self.stdout.write("Creating demo drug inventory scenarios...")

        # 1. OUT OF STOCK DRUGS
        drug_out_of_stock = Drug.objects.create(
            pharmacy=pharmacy,
            name='Amoxicillin',
            brand='Amoxil',
            description='Antibiotic used to treat bacterial infections',
            dosage='500mg capsules',
            route='Oral',
            stock=0,
            status='out_of_stock',
            resupply_pending=False
        )
        drug_out_of_stock.update_status()
        drug_out_of_stock.save()

        # 2. OUT OF STOCK WITH RESUPPLY PENDING
        drug_out_pending = Drug.objects.create(
            pharmacy=pharmacy,
            name='Lisinopril',
            brand='Prinivil',
            description='ACE inhibitor for high blood pressure',
            dosage='10mg tablets',
            route='Oral',
            stock=0,
            status='out_of_stock',
            resupply_pending=True
        )
        drug_out_pending.update_status()
        drug_out_pending.save()

        # 3. LOW STOCK DRUGS
        drug_low_stock1 = Drug.objects.create(
            pharmacy=pharmacy,
            name='Metformin',
            brand='Glucophage',
            description='Diabetes medication',
            dosage='500mg tablets',
            route='Oral',
            stock=15,
            status='low_stock',
            resupply_pending=False
        )
        drug_low_stock1.update_status()
        drug_low_stock1.save()

        drug_low_stock2 = Drug.objects.create(
            pharmacy=pharmacy,
            name='Atorvastatin',
            brand='Lipitor',
            description='Cholesterol medication',
            dosage='20mg tablets',
            route='Oral',
            stock=25,
            status='low_stock',
            resupply_pending=False
        )
        drug_low_stock2.update_status()
        drug_low_stock2.save()

        # 4. IN STOCK DRUGS
        drug_in_stock1 = Drug.objects.create(
            pharmacy=pharmacy,
            name='Omeprazole',
            brand='Prilosec',
            description='Proton pump inhibitor for acid reflux',
            dosage='20mg capsules',
            route='Oral',
            stock=150,
            status='in_stock',
            resupply_pending=False
        )
        drug_in_stock1.update_status()
        drug_in_stock1.save()

        drug_in_stock2 = Drug.objects.create(
            pharmacy=pharmacy,
            name='Levothyroxine',
            brand='Synthroid',
            description='Thyroid hormone replacement',
            dosage='50mcg tablets',
            route='Oral',
            stock=200,
            status='in_stock',
            resupply_pending=False
        )
        drug_in_stock2.update_status()
        drug_in_stock2.save()

        self.stdout.write(self.style.SUCCESS(f"✓ Created inventory: 2 out of stock, 2 low stock, 2 in stock"))

        # Create Prescriptions
        self.stdout.write("Creating prescriptions...")

        # Active prescriptions
        rx1 = Prescription.objects.create(
            patient=patient1,
            medicine=drug_in_stock1,
            quantity=30,
            prescribed_by=pharmacist,
            expiration_date=date.today() + timedelta(days=180),
            refills_left=3,
            refill_pending=False
        )

        rx2 = Prescription.objects.create(
            patient=patient1,
            medicine=drug_low_stock1,
            quantity=60,
            prescribed_by=pharmacist,
            expiration_date=date.today() + timedelta(days=180),
            refills_left=2,
            refill_pending=False
        )

        # Prescription with refill pending
        rx3 = Prescription.objects.create(
            patient=patient2,
            medicine=drug_in_stock2,
            quantity=30,
            prescribed_by=pharmacist,
            expiration_date=date.today() + timedelta(days=90),
            refills_left=1,
            refill_pending=True
        )

        # Prescription for out of stock drug
        rx4 = Prescription.objects.create(
            patient=patient2,
            medicine=drug_out_of_stock,
            quantity=20,
            prescribed_by=pharmacist,
            expiration_date=date.today() + timedelta(days=60),
            refills_left=0,
            refill_pending=False
        )

        # Prescription about to expire
        rx5 = Prescription.objects.create(
            patient=patient3,
            medicine=drug_low_stock2,
            quantity=30,
            prescribed_by=pharmacist,
            expiration_date=date.today() + timedelta(days=15),
            refills_left=0,
            refill_pending=False
        )

        self.stdout.write(self.style.SUCCESS(f"✓ Created 5 prescriptions (1 with refill pending, 1 expiring soon)"))

        # Create Medication Reminders
        self.stdout.write("Creating medication reminders...")

        # 1. ACTIVE REMINDERS
        reminder1 = MedicationReminder.objects.create(
            user=patient1,
            prescription=rx1,
            frequency=2,
            start_date=date.today() - timedelta(days=10),
            day_amount=30,
            is_active=True,
            is_archived=False,
            remaining_days=20
        )
        ReminderTime.objects.create(reminder=reminder1, time=time(9, 0), is_active=True)
        ReminderTime.objects.create(reminder=reminder1, time=time(21, 0), is_active=True)

        reminder2 = MedicationReminder.objects.create(
            user=patient1,
            prescription=rx2,
            frequency=1,
            start_date=date.today() - timedelta(days=5),
            day_amount=60,
            is_active=True,
            is_archived=False,
            remaining_days=55
        )
        ReminderTime.objects.create(reminder=reminder2, time=time(8, 30), is_active=True)

        # 2. REMINDER RUNNING OUT (3 days left)
        reminder3 = MedicationReminder.objects.create(
            user=patient2,
            prescription=rx3,
            frequency=1,
            start_date=date.today() - timedelta(days=27),
            day_amount=30,
            is_active=True,
            is_archived=False,
            remaining_days=3
        )
        ReminderTime.objects.create(reminder=reminder3, time=time(10, 0), is_active=True)

        # 3. ARCHIVED REMINDERS
        reminder4 = MedicationReminder.objects.create(
            user=patient1,
            prescription=rx1,
            frequency=3,
            start_date=date.today() - timedelta(days=60),
            day_amount=30,
            is_active=False,
            is_archived=True,
            remaining_days=0,
            restoration_time=timezone.now() - timedelta(days=30)
        )
        ReminderTime.objects.create(reminder=reminder4, time=time(8, 0), is_active=False)
        ReminderTime.objects.create(reminder=reminder4, time=time(14, 0), is_active=False)
        ReminderTime.objects.create(reminder=reminder4, time=time(20, 0), is_active=False)

        reminder5 = MedicationReminder.objects.create(
            user=patient2,
            prescription=rx4,
            frequency=2,
            start_date=date.today() - timedelta(days=45),
            day_amount=20,
            is_active=False,
            is_archived=True,
            remaining_days=0,
            restoration_time=timezone.now() - timedelta(days=25)
        )
        ReminderTime.objects.create(reminder=reminder5, time=time(9, 0), is_active=False)
        ReminderTime.objects.create(reminder=reminder5, time=time(21, 0), is_active=False)

        reminder6 = MedicationReminder.objects.create(
            user=patient3,
            prescription=rx5,
            frequency=1,
            start_date=date.today() - timedelta(days=90),
            day_amount=30,
            is_active=False,
            is_archived=True,
            remaining_days=0,
            restoration_time=timezone.now() - timedelta(days=60)
        )
        ReminderTime.objects.create(reminder=reminder6, time=time(12, 0), is_active=False)

        self.stdout.write(self.style.SUCCESS(f"✓ Created 6 reminders (3 active, 3 archived, 1 running out soon)"))

        # Create Message Threads and Messages
        self.stdout.write("Creating message threads and conversations...")

        # Thread 1: Patient requesting refill
        thread1 = Thread.objects.create()
        thread1.participant.add(patient2.user, pharmacist_user)

        msg1 = Message.objects.create(
            sender=patient2.user,
            recipient=pharmacist_user,
            thread=thread1,
            content=f"Hi, I need a refill for my {drug_in_stock2.brand} prescription. I'm running low.",
            timestamp=timezone.now() - timedelta(hours=3),
            prescription=rx3,
            refill_fulfilled=None
        )
        ReadStatus.objects.create(message=msg1, user=pharmacist_user, read=False)
        ReadStatus.objects.create(message=msg1, user=patient2.user, read=True)

        msg2 = Message.objects.create(
            sender=pharmacist_user,
            recipient=patient2.user,
            thread=thread1,
            content="I've received your refill request. We'll have it ready for pickup tomorrow.",
            timestamp=timezone.now() - timedelta(hours=2),
            prescription=rx3,
            refill_fulfilled=True
        )
        ReadStatus.objects.create(message=msg2, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg2, user=patient2.user, read=False)

        # Thread 2: Patient asking about out of stock medication
        thread2 = Thread.objects.create()
        thread2.participant.add(patient2.user, pharmacist_user)

        msg3 = Message.objects.create(
            sender=patient2.user,
            recipient=pharmacist_user,
            thread=thread2,
            content=f"Do you have {drug_out_of_stock.brand} in stock? I need to fill my prescription.",
            timestamp=timezone.now() - timedelta(days=1, hours=5),
            drug=drug_out_of_stock
        )
        ReadStatus.objects.create(message=msg3, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg3, user=patient2.user, read=True)

        msg4 = Message.objects.create(
            sender=pharmacist_user,
            recipient=patient2.user,
            thread=thread2,
            content=f"Unfortunately, {drug_out_of_stock.brand} is currently out of stock. We're waiting for a resupply. I'll notify you when it arrives.",
            timestamp=timezone.now() - timedelta(days=1, hours=4),
            drug=drug_out_of_stock,
            resupply_fulfilled=False
        )
        ReadStatus.objects.create(message=msg4, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg4, user=patient2.user, read=True)

        msg5 = Message.objects.create(
            sender=patient2.user,
            recipient=pharmacist_user,
            thread=thread2,
            content="Thank you for letting me know. Please keep me updated.",
            timestamp=timezone.now() - timedelta(days=1, hours=3),
        )
        ReadStatus.objects.create(message=msg5, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg5, user=patient2.user, read=True)

        # Thread 3: Patient asking about low stock medication
        thread3 = Thread.objects.create()
        thread3.participant.add(patient1.user, pharmacist_user)

        msg6 = Message.objects.create(
            sender=pharmacist_user,
            recipient=patient1.user,
            thread=thread3,
            content=f"Hi {patient1.first_name}, just wanted to let you know that {drug_low_stock1.brand} is running low in our inventory. Please refill your prescription soon.",
            timestamp=timezone.now() - timedelta(hours=12),
            drug=drug_low_stock1
        )
        ReadStatus.objects.create(message=msg6, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg6, user=patient1.user, read=False)

        # Thread 4: General inquiry (older, read conversation)
        thread4 = Thread.objects.create()
        thread4.participant.add(patient3.user, pharmacist_user)

        msg7 = Message.objects.create(
            sender=patient3.user,
            recipient=pharmacist_user,
            thread=thread4,
            content="What are your pharmacy hours on weekends?",
            timestamp=timezone.now() - timedelta(days=3),
        )
        ReadStatus.objects.create(message=msg7, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg7, user=patient3.user, read=True)

        msg8 = Message.objects.create(
            sender=pharmacist_user,
            recipient=patient3.user,
            thread=thread4,
            content="We're open Saturday 9am-5pm and Sunday 10am-4pm. Let me know if you need anything!",
            timestamp=timezone.now() - timedelta(days=3) + timedelta(minutes=15),
        )
        ReadStatus.objects.create(message=msg8, user=pharmacist_user, read=True)
        ReadStatus.objects.create(message=msg8, user=patient3.user, read=True)

        self.stdout.write(self.style.SUCCESS(f"✓ Created 4 message threads with 8 messages (some unread)"))

        # Create Notifications
        self.stdout.write("Creating notifications...")

        # Unread notifications for pharmacist about refill requests
        notif1 = Notifications.objects.create(
            user=pharmacist_user,
            message=msg1,
            content=f"New refill request from {patient2.first_name} {patient2.last_name}",
            link=f"/pharmacy/prescriptions/{rx3.id}/",
            prescription=rx3,
            time=timezone.now() - timedelta(hours=3),
            is_read=False
        )

        # Unread notification for patient about low stock
        notif2 = Notifications.objects.create(
            user=patient1.user,
            message=msg6,
            content=f"Low stock alert for {drug_low_stock1.brand}",
            link=f"/patients/prescriptions/",
            drug=drug_low_stock1,
            time=timezone.now() - timedelta(hours=12),
            is_read=False
        )

        # Read notification about message response
        notif3 = Notifications.objects.create(
            user=patient2.user,
            message=msg2,
            content=f"Pharmacist responded to your refill request",
            link=f"/patients/messages/",
            prescription=rx3,
            time=timezone.now() - timedelta(hours=2),
            is_read=True
        )

        # Notification about reminder running out
        notif4 = Notifications.objects.create(
            user=patient2.user,
            reminder=reminder3,
            content=f"Your {drug_in_stock2.brand} reminder expires in 3 days",
            link=f"/patients/reminders/",
            time=timezone.now() - timedelta(hours=6),
            is_read=False
        )

        # Notification about out of stock
        notif5 = Notifications.objects.create(
            user=pharmacist_user,
            drug=drug_out_of_stock,
            content=f"{drug_out_of_stock.brand} is out of stock",
            link=f"/pharmacy/inventory/",
            time=timezone.now() - timedelta(days=1),
            is_read=True
        )

        self.stdout.write(self.style.SUCCESS(f"✓ Created 5 notifications (2 unread)"))

        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("DEMO DATA SUMMARY"))
        self.stdout.write("="*60)
        self.stdout.write(f"📦 Inventory:")
        self.stdout.write(f"   - Out of stock: {drug_out_of_stock.brand}, {drug_out_pending.brand} (resupply pending)")
        self.stdout.write(f"   - Low stock: {drug_low_stock1.brand} ({drug_low_stock1.stock} left), {drug_low_stock2.brand} ({drug_low_stock2.stock} left)")
        self.stdout.write(f"   - In stock: {drug_in_stock1.brand}, {drug_in_stock2.brand}")
        self.stdout.write(f"\n💊 Prescriptions:")
        self.stdout.write(f"   - Total: 5 prescriptions")
        self.stdout.write(f"   - 1 with refill pending")
        self.stdout.write(f"   - 1 expiring in 15 days")
        self.stdout.write(f"\n⏰ Medication Reminders:")
        self.stdout.write(f"   - Active: 3 reminders")
        self.stdout.write(f"   - Archived: 3 reminders")
        self.stdout.write(f"   - 1 reminder running out (3 days left)")
        self.stdout.write(f"\n💬 Messages:")
        self.stdout.write(f"   - 4 conversation threads")
        self.stdout.write(f"   - 8 total messages")
        self.stdout.write(f"   - Mix of read/unread messages")
        self.stdout.write(f"\n🔔 Notifications:")
        self.stdout.write(f"   - 5 notifications (2 unread)")
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS("\n✓ Demo scenarios seeded successfully!"))
