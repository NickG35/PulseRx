#!/usr/bin/env python3
"""
Export SQLite database to JSON format that can be loaded into production
"""
import sqlite3
import json
from datetime import datetime

def export_sqlite_to_json():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    data = []

    # Tables to export (in order to respect foreign keys)
    tables_to_export = [
        ('auth_group', 'auth.group'),
        ('accounts_customaccount', 'accounts.customaccount'),
        ('patients_patientprofile', 'patients.patientprofile'),
        ('pharmacy_pharmacyprofile', 'pharmacy.pharmacyprofile'),
        ('pharmacy_pharmacistprofile', 'pharmacy.pharmacistprofile'),
        ('pharmacy_drug', 'pharmacy.drug'),
        ('pharmacy_prescription', 'pharmacy.prescription'),
        ('patients_medicationreminder', 'patients.medicationreminder'),
        ('patients_remindertime', 'patients.remindertime'),
        ('pharmacy_message', 'pharmacy.message'),
        ('accounts_notifications', 'accounts.notifications'),
        ('accounts_thread', 'accounts.thread'),
        ('accounts_thread_participant', 'accounts.thread_participant'),
        ('accounts_readstatus', 'accounts.readstatus'),
    ]

    for table_name, model_name in tables_to_export:
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            for row in rows:
                fields = {}
                for key in row.keys():
                    if key == 'id':
                        continue  # Skip id, let Django auto-assign
                    value = row[key]
                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')
                    fields[key] = value

                data.append({
                    "model": model_name,
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
    print("\nTo load this data in production:")
    print("1. Upload production_data.json to your Render web service")
    print("2. Run in Render Shell: python manage.py loaddata production_data.json")

if __name__ == '__main__':
    export_sqlite_to_json()
