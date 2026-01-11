#!/usr/bin/env python3
"""
Export SQLite database to JSON format with field length truncation
"""
import sqlite3
import json

def truncate_field(value, max_length):
    """Truncate a string value to max_length"""
    if value and isinstance(value, str) and len(value) > max_length:
        return value[:max_length]
    return value

def export_sqlite_to_json():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    data = []

    # Tables to export (in order to respect foreign keys)
    # IMPORTANT: Order matters! Dependencies must come before dependents
    tables_to_export = [
        ('auth_group', 'auth.group', {}),
        ('accounts_customaccount', 'accounts.customaccount', {}),
        ('pharmacy_pharmacyprofile', 'pharmacy.pharmacyprofile', {}),  # Must come before patients/pharmacists
        ('pharmacy_pharmacistprofile', 'pharmacy.pharmacistprofile', {}),
        ('patients_patientprofile', 'patients.patientprofile', {}),  # Depends on pharmacy
        ('pharmacy_drug', 'pharmacy.drug', {'dosage': 100, 'route': 100}),  # Truncate these fields
        ('pharmacy_prescription', 'pharmacy.prescription', {}),
        ('patients_medicationreminder', 'patients.medicationreminder', {}),
        ('patients_remindertime', 'patients.remindertime', {}),
        ('accounts_thread', 'accounts.thread', {}),  # Must come before thread_participant and messages
        ('accounts_thread_participant', 'accounts.thread_participant', {}),
        ('pharmacy_message', 'pharmacy.message', {}),
        ('accounts_notifications', 'accounts.notifications', {}),
        ('accounts_readstatus', 'accounts.readstatus', {}),
    ]

    for table_info in tables_to_export:
        table_name = table_info[0]
        model_name = table_info[1]
        field_limits = table_info[2] if len(table_info) > 2 else {}

        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            for row in rows:
                fields = {}
                pk = None
                for key in row.keys():
                    value = row[key]

                    # Capture id as pk for the fixture
                    if key == 'id':
                        pk = value
                        continue

                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')

                    # Truncate fields if they exceed limits
                    if key in field_limits:
                        value = truncate_field(value, field_limits[key])

                    fields[key] = value

                data.append({
                    "model": model_name,
                    "pk": pk,
                    "fields": fields
                })

            print(f"Exported {len(rows)} rows from {table_name}")
        except sqlite3.OperationalError as e:
            print(f"Skipping {table_name}: {e}")
            continue

    conn.close()

    # Write to JSON file
    with open('production_data.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"\nTotal records exported: {len(data)}")
    print("Data saved to production_data.json")
    print("\nNote: Long dosage and route fields were truncated to 100 characters")
    print("\nTo load this data in production:")
    print("Run in Render Shell: python manage.py loaddata production_data.json")

if __name__ == '__main__':
    export_sqlite_to_json()
