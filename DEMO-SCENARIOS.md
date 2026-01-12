# Quick Demo Scenarios Reference

## 🚀 Quick Start

```bash
./seed_demo.sh
```

## 📋 What You'll See

### Inventory Page (Pharmacist)
- ❌ **2 Out of Stock**: Amoxil, Prinivil (1 has resupply pending)
- ⚠️ **2 Low Stock**: Glucophage (15 left), Lipitor (25 left)
- ✅ **2 In Stock**: Prilosec (150), Synthroid (200)

### Messages Page
**Unread Messages:**
- Patient 1: Unread pharmacist response about low stock alert
- Patient 2: Unread pharmacist response about refill

**Read Conversations:**
- Out of stock medication inquiry (Amoxil)
- General pharmacy hours question

### Reminders Page (Patient View)
**Active:**
- 2 reminders with days remaining
- 1 reminder **expiring in 3 days** ⏰

**Archived Tab:**
- 3 completed medication schedules from past prescriptions

### Notifications
**Unread:**
- Pharmacist: New refill request
- Patient: Low stock alert
- Patient: Reminder expiring soon

**Read:**
- Refill fulfilled
- Out of stock notification

## 🎯 Demo Flow Ideas

### Scenario 1: Inventory Management
1. Login as pharmacist
2. Navigate to Inventory
3. Point out the stock status colors (red, yellow, green)
4. Show "Resupply Pending" flag on Prinivil
5. Demonstrate marking low stock items for resupply

### Scenario 2: Patient Medication Tracking
1. Login as patient
2. View active reminders dashboard
3. Show reminder times (multiple times per day)
4. Navigate to archived reminders to show history
5. Point out the "3 days remaining" warning

### Scenario 3: Refill Request Workflow
1. Patient tab: Request refill for a prescription
2. Switch to Pharmacist tab: See new notification
3. Pharmacist: Approve/process refill
4. Switch back to Patient tab: See confirmation

### Scenario 4: Messaging System
1. Show unread message count in navigation
2. Open message thread
3. Demonstrate real-time conversation history
4. Show linked prescriptions in messages
5. Reply to message

### Scenario 5: Stock Alerts
1. Pharmacist view: Low stock notification
2. Navigate to inventory from notification
3. Show drug details
4. Mark for resupply
5. Send message to patients with that prescription

## 👥 Test Accounts

Find existing accounts in your database:
```bash
python manage.py shell
>>> from accounts.models import CustomAccount
>>> CustomAccount.objects.filter(role='pharmacist').values('username', 'first_name', 'last_name')
>>> CustomAccount.objects.filter(role='patient').values('username', 'first_name', 'last_name')
```

Default password for demo accounts: `pharmacist123` or `patient123`

## 🔄 Reset Demo Data

To reset and recreate demo data:
```bash
# Clear existing demo drugs (optional)
python manage.py shell
>>> from pharmacy.models import Drug
>>> Drug.objects.filter(brand__in=['Amoxil', 'Prinivil', 'Glucophage', 'Lipitor', 'Prilosec', 'Synthroid']).delete()
>>> exit()

# Reseed
./seed_demo.sh
```

## 💡 Feature Highlights During Demo

✅ **Real-time notifications** - Show bell icon badge count
✅ **Read/unread status** - Messages and notifications track read state
✅ **Stock status automation** - Colors update based on quantity
✅ **Reminder archiving** - Automatic archiving when complete
✅ **Multi-role messaging** - Patient-pharmacist communication
✅ **Prescription tracking** - Refills, expiration dates, quantities
✅ **Medication adherence** - Multiple daily reminder times
✅ **Inventory management** - Stock levels, resupply workflow

## 🎨 Visual Indicators to Point Out

- 🔴 Red badges for urgent items (out of stock, expiring soon)
- 🟡 Yellow badges for warnings (low stock)
- 🟢 Green indicators for healthy status
- 🔔 Notification badge counts
- 💬 Unread message indicators
- ⏰ Days remaining counters
- ⚠️ "Resupply Pending" flags
