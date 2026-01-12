# 🚀 PulseRx Demo - Quick Start Guide

## Step 1: Seed Demo Data

```bash
./seed_demo.sh
```

This creates:
- ✅ 6 drugs (2 out of stock, 2 low stock, 2 in stock)
- ✅ 5 prescriptions (various states)
- ✅ 6 medication reminders (3 active, 3 archived)
- ✅ 4 message threads with 8 messages
- ✅ 5 notifications (mix of read/unread)

## Step 2: Get Your Test Accounts

```bash
python show_demo_accounts.py
```

This shows all available accounts with usernames and passwords.

**Quick Access:**
- **Pharmacist**: `ngeorge` / `pharmacist123`
- **Patient 1**: `jjackson` / `patient123`
- **Patient 2**: `acamacho` / `patient123`

## Step 3: Open Multiple Browser Sessions

### Method 1: Regular + Incognito (Easiest)
1. **Chrome Regular Tab**: Login as Pharmacist (`ngeorge`)
2. **Chrome Incognito**: Login as Patient (`jjackson`)

### Method 2: Different Browser Profiles
1. **Chrome Profile 1**: Pharmacist
2. **Chrome Profile 2**: Patient 1
3. **Chrome Profile 3**: Patient 2

### Method 3: Different Browsers
1. **Chrome**: Pharmacist
2. **Firefox**: Patient
3. **Safari**: Admin

## Step 4: Demo Flows

### Flow A: Inventory & Stock Management (Pharmacist View)

1. **Login** as pharmacist: `ngeorge`
2. **Navigate to Inventory**
3. **Observe:**
   - 🔴 **Amoxil** - Out of stock
   - 🔴 **Prinivil** - Out of stock (resupply pending ✓)
   - 🟡 **Glucophage** - Low stock (15 left)
   - 🟡 **Lipitor** - Low stock (25 left)
   - 🟢 **Prilosec** - In stock (150)
   - 🟢 **Synthroid** - In stock (200)

### Flow B: Patient Reminders (Patient View)

1. **Login** as patient: `jjackson`
2. **Navigate to Reminders**
3. **View Active Reminders:**
   - See 3 active medication reminders
   - Notice one is expiring soon (⚠️ 3 days left)
4. **Click "View Archived"**
   - See completed medication schedules from the past

### Flow C: Messaging & Refills (Both Views)

**Patient Side:**
1. Login as `acamacho`
2. Check notifications (unread message)
3. Open messages
4. View conversation about Synthroid refill

**Pharmacist Side:**
1. Login as `ngeorge` (different browser/incognito)
2. Check notifications (refill request)
3. Review prescription
4. Process refill

### Flow D: Stock Alerts (Pharmacist → Patient)

**Pharmacist Side:**
1. Check notifications
2. See low stock alert for Glucophage
3. View patients with that prescription

**Patient Side:**
1. Patient has unread notification about low stock
2. Shows proactive pharmacy communication

## Common Demo Talking Points

### 🎯 Real-time Features
- "Notice how notifications appear instantly without refreshing"
- "WebSocket connections keep everything in sync"

### 📊 Inventory Management
- "Color-coded stock levels (red/yellow/green) for quick visual scanning"
- "Resupply pending flags to track replenishment"

### 💊 Medication Adherence
- "Patients can set multiple reminder times per day"
- "Automatic archiving when medication schedule completes"
- "Visual indicators for reminders running out"

### 💬 Communication
- "Direct messaging between patients and pharmacists"
- "Read receipts and unread counts"
- "Message threads linked to prescriptions"

### 🔔 Smart Notifications
- "Contextual notifications with quick links"
- "Unread badge counts across the system"
- "Auto-marking as read when viewing"

## Testing Checklist

- [ ] Login with multiple roles simultaneously
- [ ] Check inventory status colors
- [ ] View active and archived reminders
- [ ] Read/send messages between patient and pharmacist
- [ ] Check notification counts and states
- [ ] Navigate using notification links
- [ ] View prescription details
- [ ] Check refill request workflow

## Troubleshooting

**Issue**: Can't login with second account in same browser
- **Solution**: Use incognito window or different browser profile

**Issue**: No demo data showing
- **Solution**: Run `./seed_demo.sh` again

**Issue**: Want to see which accounts exist
- **Solution**: Run `python show_demo_accounts.py`

**Issue**: Want fresh demo data
- **Solution**: Delete demo drugs and reseed:
  ```bash
  python manage.py shell
  >>> from pharmacy.models import Drug
  >>> Drug.objects.filter(brand__in=['Amoxil', 'Prinivil', 'Glucophage', 'Lipitor', 'Prilosec', 'Synthroid']).delete()
  >>> exit()
  ./seed_demo.sh
  ```

## Additional Resources

- **Full Testing Workflows**: See [DEMO-SCENARIOS.md](DEMO-SCENARIOS.md)
- **Complete Data Guide**: See [DEMO-DATA-GUIDE.md](DEMO-DATA-GUIDE.md)
- **Development Setup**: See [README.md](README.md)

---

**Happy Testing! 🎉**
