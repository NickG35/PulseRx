# Demo Data Guide

This guide explains the demo data scenarios created for PulseRx demonstrations.

## Running the Demo Data Seeder

```bash
# Option 1: Use the shell script
./seed_demo.sh

# Option 2: Run directly
python manage.py seed_demo_scenarios
```

## What Gets Created

### 📦 Inventory Scenarios

1. **Out of Stock Items**
   - **Amoxil (Amoxicillin 500mg)** - Out of stock, no resupply pending
   - **Prinivil (Lisinopril 10mg)** - Out of stock, resupply pending ✅

2. **Low Stock Items**
   - **Glucophage (Metformin 500mg)** - 15 units remaining ⚠️
   - **Lipitor (Atorvastatin 20mg)** - 25 units remaining ⚠️

3. **In Stock Items**
   - **Prilosec (Omeprazole 20mg)** - 150 units
   - **Synthroid (Levothyroxine 50mcg)** - 200 units

### 💊 Prescription Scenarios

- **5 total prescriptions** created across 3 patients
- **1 prescription with refill pending** (Synthroid for Patient 2)
- **1 prescription expiring soon** (15 days - Lipitor for Patient 3)
- **1 prescription for out-of-stock drug** (Amoxil)

### ⏰ Medication Reminder Scenarios

#### Active Reminders (3)
1. **Patient 1 - Prilosec**: 2x daily (9am, 9pm), 20 days remaining
2. **Patient 1 - Glucophage**: 1x daily (8:30am), 55 days remaining
3. **Patient 2 - Synthroid**: 1x daily (10am), **3 days remaining** ⚠️

#### Archived Reminders (3)
4. **Patient 1 - Prilosec**: 3x daily, completed 30 days ago
5. **Patient 2 - Amoxil**: 2x daily, completed 25 days ago
6. **Patient 3 - Lipitor**: 1x daily, completed 60 days ago

### 💬 Message Thread Scenarios

#### Thread 1: Active Refill Request (Unread by Patient)
- Patient 2 requests Synthroid refill
- Pharmacist confirms it will be ready tomorrow
- **Patient has unread response**

#### Thread 2: Out of Stock Inquiry (All Read)
- Patient 2 asks about Amoxil availability
- Pharmacist explains it's out of stock, waiting for resupply
- Patient thanks and asks to be updated

#### Thread 3: Low Stock Alert (Unread by Patient)
- Pharmacist proactively notifies Patient 1 about low Glucophage stock
- **Patient hasn't read the message yet**

#### Thread 4: General Inquiry (All Read - Older)
- Patient 3 asks about weekend hours
- Pharmacist provides hours
- 3 days old, fully read conversation

### 🔔 Notification Scenarios

1. **Unread Pharmacist Notification**: New refill request from Patient 2
2. **Unread Patient Notification**: Low stock alert for Glucophage
3. **Read Patient Notification**: Pharmacist responded to refill request
4. **Unread Patient Notification**: Reminder expiring in 3 days
5. **Read Pharmacist Notification**: Out of stock alert for Amoxil

## Demo Flow Suggestions

### For Pharmacist Role Demo
1. **Check inventory** → See low stock and out of stock items
2. **View notifications** → See unread refill request
3. **Check messages** → Respond to patient inquiries
4. **Mark out-of-stock item as resupply pending**

### For Patient Role Demo
1. **Check reminders** → See active reminders and one expiring soon
2. **View archived reminders** → Show history of completed medication schedules
3. **Check messages** → See unread response from pharmacist
4. **Check notifications** → See low stock alert
5. **Request refill** → Test refill request functionality

### Multi-Tab Testing Scenarios
- **Tab 1 (Pharmacist)**: View refill requests and respond
- **Tab 2 (Patient)**: Request refill and check for response
- **Tab 3 (Different Patient)**: View their own reminders and messages

## Key Features to Showcase

✅ **Inventory Management**: Out of stock, low stock, in stock states
✅ **Stock Alerts**: Resupply pending flags
✅ **Medication Reminders**: Active, archived, and expiring states
✅ **Real-time Messaging**: Patient-pharmacist communication
✅ **Refill Requests**: Pending and fulfilled states
✅ **Notifications**: Read/unread status tracking
✅ **Prescription Management**: Active, expiring, and out-of-stock scenarios

## Notes

- All demo users use password: `pharmacist123` or `patient123`
- Timestamps are relative to the current time
- The script requires existing pharmacy and patient profiles
- Run `python manage.py seed_fake_data` first if you need to create initial users
