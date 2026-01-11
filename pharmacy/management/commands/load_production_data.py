"""
Management command to load production data from JSON file.
This avoids database schema issues by using Django ORM directly.

Usage:
    python manage.py load_production_data [--file path/to/data.json]
"""
import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomAccount, Message, Thread
from pharmacy.models import PharmacyProfile, PharmacistProfile, Drug, Prescription
from patients.models import PatientProfile

CustomUser = get_user_model()


class Command(BaseCommand):
    help = 'Load production data from JSON file using Django ORM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='production_data.json',
            help='Path to the JSON data file (default: production_data.json)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'File "{file_path}" not found')
        except json.JSONDecodeError:
            raise CommandError(f'Invalid JSON in file "{file_path}"')

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS(f'Loading data from {file_path}...'))

        # Process data in dependency order
        with transaction.atomic():
            stats = {
                'users': 0,
                'pharmacies': 0,
                'pharmacists': 0,
                'patients': 0,
                'drugs': 0,
                'prescriptions': 0,
                'threads': 0,
                'messages': 0,
            }

            # Track PKs for reference
            pk_map = {}

            for item in data:
                model_name = item.get('model')
                pk = item.get('pk')
                fields = item.get('fields', {})

                if not model_name or not fields:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping invalid item: {item}')
                    )
                    continue

                try:
                    if model_name == 'accounts.customaccount':
                        obj = self.load_user(pk, fields)
                        if pk:
                            pk_map[f'user_{pk}'] = obj.pk
                        stats['users'] += 1

                    elif model_name == 'pharmacy.pharmacyprofile':
                        obj = self.load_pharmacy(pk, fields, pk_map)
                        if pk:
                            pk_map[f'pharmacy_{pk}'] = obj.pk
                        stats['pharmacies'] += 1

                    elif model_name == 'pharmacy.pharmacistprofile':
                        obj = self.load_pharmacist(pk, fields, pk_map)
                        if pk:
                            pk_map[f'pharmacist_{pk}'] = obj.pk
                        stats['pharmacists'] += 1

                    elif model_name == 'patients.patientprofile':
                        obj = self.load_patient(pk, fields, pk_map)
                        if pk:
                            pk_map[f'patient_{pk}'] = obj.pk
                        stats['patients'] += 1

                    elif model_name == 'pharmacy.drug':
                        obj = self.load_drug(pk, fields, pk_map)
                        if pk:
                            pk_map[f'drug_{pk}'] = obj.pk
                        stats['drugs'] += 1

                    elif model_name == 'pharmacy.prescription':
                        obj = self.load_prescription(pk, fields, pk_map)
                        if pk:
                            pk_map[f'prescription_{pk}'] = obj.pk
                        stats['prescriptions'] += 1

                    elif model_name == 'accounts.thread':
                        obj = self.load_thread(pk, fields, pk_map)
                        if pk:
                            pk_map[f'thread_{pk}'] = obj.pk
                        stats['threads'] += 1

                    elif model_name == 'accounts.message':
                        obj = self.load_message(pk, fields, pk_map)
                        if pk:
                            pk_map[f'message_{pk}'] = obj.pk
                        stats['messages'] += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error loading {model_name} (pk={pk}): {str(e)}')
                    )
                    raise

        # Print statistics
        self.stdout.write(self.style.SUCCESS('\nData loaded successfully:'))
        for model, count in stats.items():
            if count > 0:
                self.stdout.write(f'  {model.capitalize()}: {count}')

    def clear_data(self):
        """Clear existing data"""
        Prescription.objects.all().delete()
        Message.objects.all().delete()
        Drug.objects.all().delete()
        PatientProfile.objects.all().delete()
        PharmacistProfile.objects.all().delete()
        PharmacyProfile.objects.all().delete()
        CustomAccount.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

    def load_user(self, pk, fields):
        """Load or update a CustomAccount"""
        obj, created = CustomAccount.objects.update_or_create(
            username=fields['username'],
            defaults={
                'email': fields.get('email', ''),
                'first_name': fields.get('first_name', ''),
                'last_name': fields.get('last_name', ''),
                'is_active': fields.get('is_active', True),
                'is_staff': fields.get('is_staff', False),
                'is_superuser': fields.get('is_superuser', False),
                'date_joined': fields.get('date_joined'),
                'role': fields.get('role', 'patient'),
            }
        )
        # Set password and last_login if provided
        update_fields = []
        if 'password' in fields:
            obj.password = fields['password']
            update_fields.append('password')
        if 'last_login' in fields and fields['last_login']:
            obj.last_login = fields['last_login']
            update_fields.append('last_login')
        if update_fields:
            obj.save(update_fields=update_fields)
        return obj

    def load_pharmacy(self, pk, fields, pk_map):
        """Load or update a PharmacyProfile"""
        user_pk = pk_map.get(f'user_{fields.get("user_id")}') if fields.get("user_id") else None
        user = CustomAccount.objects.get(pk=user_pk) if user_pk else None

        obj, created = PharmacyProfile.objects.update_or_create(
            user=user,
            defaults={
                'pharmacy_name': fields['pharmacy_name'],
                'street_address': fields.get('street_address', ''),
                'city': fields.get('city', ''),
                'state': fields.get('state', ''),
                'zip_code': fields.get('zip_code', ''),
                'join_code': fields.get('join_code', ''),
            }
        )
        return obj

    def load_pharmacist(self, pk, fields, pk_map):
        """Load or update a PharmacistProfile"""
        user_pk = pk_map.get(f'user_{fields.get("user_id")}') if fields.get("user_id") else None
        pharmacy_pk = pk_map.get(f'pharmacy_{fields.get("pharmacy_id")}') if fields.get("pharmacy_id") else None

        user = CustomAccount.objects.get(pk=user_pk) if user_pk else None
        pharmacy = PharmacyProfile.objects.get(pk=pharmacy_pk) if pharmacy_pk else None

        obj, created = PharmacistProfile.objects.update_or_create(
            user=user,
            defaults={
                'pharmacy': pharmacy,
                'first_name': fields['first_name'],
                'last_name': fields['last_name'],
            }
        )
        return obj

    def load_patient(self, pk, fields, pk_map):
        """Load or update a PatientProfile"""
        user_pk = pk_map.get(f'user_{fields.get("user_id")}') if fields.get("user_id") else None
        pharmacy_pk = pk_map.get(f'pharmacy_{fields.get("pharmacy_id")}') if fields.get("pharmacy_id") else None

        user = CustomAccount.objects.get(pk=user_pk) if user_pk else None
        pharmacy = PharmacyProfile.objects.get(pk=pharmacy_pk) if pharmacy_pk else None

        obj, created = PatientProfile.objects.update_or_create(
            user=user,
            defaults={
                'first_name': fields['first_name'],
                'last_name': fields['last_name'],
                'dob': fields.get('dob'),
                'gender': fields.get('gender', 'N'),
                'phone_number': fields.get('phone_number', ''),
                'pharmacy': pharmacy,
            }
        )
        return obj

    def load_drug(self, pk, fields, pk_map):
        """Load or update a Drug"""
        pharmacy_pk = pk_map.get(f'pharmacy_{fields.get("pharmacy_id")}') if fields.get("pharmacy_id") else None
        pharmacy = PharmacyProfile.objects.get(pk=pharmacy_pk) if pharmacy_pk else None

        # Truncate fields if needed (though model should handle this now)
        dosage = str(fields.get('dosage', ''))[:2000]
        route = str(fields.get('route', ''))[:255]

        obj, created = Drug.objects.update_or_create(
            name=fields['name'],
            brand=fields.get('brand', ''),
            pharmacy=pharmacy,
            defaults={
                'description': fields.get('description', ''),
                'dosage': dosage,
                'route': route,
                'stock': fields.get('stock', 100),
                'status': fields.get('status', 'in_stock'),
                'resupply_pending': fields.get('resupply_pending', False),
            }
        )
        return obj

    def load_prescription(self, pk, fields, pk_map):
        """Load or update a Prescription"""
        patient_pk = pk_map.get(f'patient_{fields.get("patient_id")}') if fields.get("patient_id") else None
        drug_pk = pk_map.get(f'drug_{fields.get("medicine_id")}') if fields.get("medicine_id") else None
        pharmacist_pk = pk_map.get(f'pharmacist_{fields.get("prescribed_by_id")}') if fields.get("prescribed_by_id") else None

        patient = PatientProfile.objects.get(pk=patient_pk) if patient_pk else None
        medicine = Drug.objects.get(pk=drug_pk) if drug_pk else None
        pharmacist = PharmacistProfile.objects.get(pk=pharmacist_pk) if pharmacist_pk else None

        obj = Prescription.objects.create(
            patient=patient,
            medicine=medicine,
            quantity=fields.get('quantity', 0),
            prescribed_by=pharmacist,
            expiration_date=fields['expiration_date'],
            refills_left=fields.get('refills_left', 3),
            refill_pending=fields.get('refill_pending', False),
        )

        # Set timestamps manually if provided
        if 'prescribed_on' in fields:
            Prescription.objects.filter(pk=obj.pk).update(prescribed_on=fields['prescribed_on'])
        if fields.get('refilled_on'):
            Prescription.objects.filter(pk=obj.pk).update(refilled_on=fields['refilled_on'])

        return obj

    def load_thread(self, pk, fields, pk_map):
        """Load or update a Thread"""
        obj = Thread.objects.create()

        # Set timestamps manually if provided
        update_fields = {}
        if 'created_at' in fields:
            update_fields['created_at'] = fields['created_at']
        if 'last_updated' in fields:
            update_fields['last_updated'] = fields['last_updated']
        if update_fields:
            Thread.objects.filter(pk=obj.pk).update(**update_fields)

        # Add participants (this is a ManyToMany relationship)
        # The fixture may have participant IDs we need to add after thread creation
        # This will be handled in a separate pass if needed

        return obj

    def load_message(self, pk, fields, pk_map):
        """Load or update a Message"""
        sender_pk = pk_map.get(f'user_{fields.get("sender_id")}') if fields.get("sender_id") else None
        recipient_pk = pk_map.get(f'user_{fields.get("recipient_id")}') if fields.get("recipient_id") else None
        thread_pk = pk_map.get(f'thread_{fields.get("thread_id")}') if fields.get("thread_id") else None
        prescription_pk = pk_map.get(f'prescription_{fields.get("prescription_id")}') if fields.get("prescription_id") else None
        drug_pk = pk_map.get(f'drug_{fields.get("drug_id")}') if fields.get("drug_id") else None

        sender = CustomAccount.objects.get(pk=sender_pk) if sender_pk else None
        recipient = CustomAccount.objects.get(pk=recipient_pk) if recipient_pk else None
        thread = Thread.objects.get(pk=thread_pk) if thread_pk else None
        prescription = Prescription.objects.get(pk=prescription_pk) if prescription_pk else None
        drug = Drug.objects.get(pk=drug_pk) if drug_pk else None

        obj = Message.objects.create(
            sender=sender,
            recipient=recipient,
            thread=thread,
            content=fields.get('content', ''),
            link=fields.get('link'),
            prescription=prescription,
            refill_fulfilled=fields.get('refill_fulfilled'),
            drug=drug,
            resupply_fulfilled=fields.get('resupply_fulfilled'),
        )

        # Set timestamp manually if provided
        if 'timestamp' in fields:
            Message.objects.filter(pk=obj.pk).update(timestamp=fields['timestamp'])

        return obj
