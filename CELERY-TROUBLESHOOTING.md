# Celery Reminder Troubleshooting Guide

## Issue: Reminder Notifications Not Sending

If your medication reminders aren't triggering notifications at the scheduled time, follow this guide.

## Quick Diagnosis

### Check 1: Is Celery Worker Running on Render?

**Problem:** Your [render.yaml](render.yaml#L32) has the worker on `plan: starter` which is a **paid plan**.

```yaml
- type: worker
  name: pulserx-worker
  runtime: python
  plan: starter  # ⚠️ This costs money!
```

**Check in Render Dashboard:**
1. Go to https://dashboard.render.com
2. Look for **pulserx-worker** in your services
3. Check if it shows as **Active** or **Suspended**

**If it's suspended/not running:**
- Reminders **will not work** because Celery tasks can't execute
- You need an active worker to process scheduled tasks

### Check 2: Are Tasks Being Created?

When you create a reminder, tasks should be scheduled in Celery. Check if they're being created:

**In your app logs (Render Dashboard → pulserx → Logs):**
```
Look for lines like:
send_reminder.apply_async(args=[123], eta=2026-01-13 10:00:00)
```

If you see these, tasks are being scheduled. If Celery worker isn't running, they won't execute.

## Solutions

### Solution 1: Enable Celery Worker (Costs Money)

If you want reminders to work on Render, you need the Celery worker running:

**Cost:** Starter plan = ~$7/month

**Steps:**
1. Render Dashboard → pulserx-worker
2. Upgrade from Free to Starter plan
3. Worker will start automatically
4. Reminders will begin working

### Solution 2: Use Render Free Plan (No Reminders)

If you want to stay on free tier:

**What Works:**
- ✅ All WebSocket features (notifications, messaging)
- ✅ Prescriptions, inventory management
- ✅ Manual refill requests
- ✅ All patient/pharmacist features

**What Doesn't Work:**
- ❌ Scheduled medication reminder notifications
- ❌ Any Celery background tasks

**Trade-off:** The app works fully except for automated reminder notifications.

### Solution 3: Alternative - Use Celery Beat + Cron Job (Free, Limited)

You could use a free cron job service to trigger reminders, but this is complex and not recommended for production.

### Solution 4: Test Locally (Development Only)

For local testing, reminders work if you run Celery:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Django
python manage.py runserver

# Terminal 3: Celery Worker
celery -A PulseRx worker --loglevel=info

# Terminal 4: Celery Beat (optional, for periodic tasks)
celery -A PulseRx beat --loglevel=info
```

## Understanding the Architecture

### How Reminders Work

1. **User creates reminder** → Django view schedules Celery task
2. **Celery task stored in Redis** → Waits for scheduled time
3. **Celery worker picks up task** → At scheduled time
4. **Task executes** → Creates notification and sends via WebSocket
5. **Patient receives notification** → In real-time

### What's Required

- ✅ **Django (Web Service)** - Running on Render Free
- ✅ **Redis** - Running on Render Free
- ✅ **WebSocket (Daphne)** - Running on Render Free
- ❌ **Celery Worker** - Needs Starter plan ($7/mo)

## Checking Celery Status

### On Render

**Check Worker Logs:**
1. Dashboard → pulserx-worker → Logs
2. Look for:
   ```
   celery@... ready.
   [tasks]
     . accounts.tasks.send_reminder
   ```

**If worker is running, you'll see:**
- Active tasks being processed
- "Received task: accounts.tasks.send_reminder[task-id]"
- "Task accounts.tasks.send_reminder[task-id] succeeded"

**If worker is NOT running:**
- Service shows as "Suspended"
- No logs
- Tasks queue up but never execute

### Locally

```bash
# Check if Celery worker is running
celery -A PulseRx inspect active

# Check scheduled tasks
celery -A PulseRx inspect scheduled

# Check registered tasks
celery -A PulseRx inspect registered
```

## Manual Testing Reminders

### Test If Task Code Works

If you want to test the reminder notification without Celery:

1. **Django Shell:**
```bash
python manage.py shell
```

2. **Import and run task manually:**
```python
from accounts.tasks import send_reminder
from patients.models import ReminderTime

# Get a reminder time
rt = ReminderTime.objects.filter(is_active=True).first()
if rt:
    print(f"Testing reminder for: {rt.reminder.prescription.medicine.name}")
    # Run task synchronously (not scheduled)
    send_reminder(rt.id)
    print("Notification should be created!")
else:
    print("No active reminder times found")
```

3. **Check if notification was created:**
```python
from accounts.models import Notifications
notif = Notifications.objects.latest('time')
print(f"Latest notification: {notif.reminder.prescription.medicine.name}")
```

### Test Full Flow Locally

1. **Start all services:**
```bash
# Terminal 1
redis-server

# Terminal 2
python manage.py runserver

# Terminal 3
celery -A PulseRx worker --loglevel=info
```

2. **Create a reminder with time in 2 minutes:**
   - Login as patient
   - Create reminder with a time 2 minutes from now
   - Watch Celery worker logs in Terminal 3

3. **Expected output in 2 minutes:**
```
[2026-01-13 10:00:00] Received task: accounts.tasks.send_reminder[...]
[2026-01-13 10:00:00] Task accounts.tasks.send_reminder[...] succeeded in 0.5s
```

4. **Check browser:**
   - Notification should appear in notification bell
   - WebSocket should send it in real-time

## Common Issues

### Issue 1: Worker on Starter Plan (Costs Money)

**Symptom:** Worker suspended, reminders don't send

**Fix Options:**
- Pay for Starter plan ($7/mo)
- Accept that reminders won't work on free tier
- Test locally only

### Issue 2: Redis Connection Error

**Symptom:** Worker can't connect to Redis

**Check:**
```python
# In Django shell
from django.conf import settings
print(settings.REDIS_URL)
# Should output: redis://...
```

**Fix:** Ensure REDIS_URL environment variable is set in both:
- Web service (pulserx)
- Worker service (pulserx-worker)

### Issue 3: Timezone Issues

**Symptom:** Reminders trigger at wrong time

**Check settings.py:**
```python
CELERY_TIMEZONE = 'America/New_York'
CELERY_ENABLE_UTC = True
```

**Fix:** Ensure timezone matches your expected time

### Issue 4: Task Not Registered

**Symptom:** "NotRegistered" error in worker logs

**Fix:** Ensure `accounts.tasks` is discovered:
```python
# PulseRx/celery.py
app.autodiscover_tasks()
```

## Recommended Approach for Demo

### For Free Tier Demo:

**What to showcase:**
1. ✅ Real-time WebSocket notifications (working)
2. ✅ Real-time messaging (working)
3. ✅ Prescription management (working)
4. ✅ Inventory tracking (working)

**What to explain:**
- "Scheduled medication reminders require a background worker"
- "This works locally and on paid hosting"
- "Demo shows the UI and reminder creation"

### For Paid Tier (Full Features):

**Enable worker:**
1. Upgrade pulserx-worker to Starter plan
2. All features work including scheduled reminders

## Files to Review

- [accounts/tasks.py](accounts/tasks.py) - Celery task definition
- [patients/views.py](patients/views.py) - Reminder scheduling logic
- [PulseRx/celery.py](PulseRx/celery.py) - Celery configuration
- [PulseRx/settings.py](PulseRx/settings.py) - Celery settings
- [render.yaml](render.yaml) - Render service configuration

## Decision Matrix

| Feature | Free Tier | Starter Plan ($7/mo) |
|---------|-----------|---------------------|
| WebSocket Notifications | ✅ Works | ✅ Works |
| Real-time Messaging | ✅ Works | ✅ Works |
| Prescription Management | ✅ Works | ✅ Works |
| Inventory Tracking | ✅ Works | ✅ Works |
| **Scheduled Reminders** | ❌ No Worker | ✅ Works |
| Background Tasks | ❌ No Worker | ✅ Works |

## Next Steps

1. **Check Render Dashboard** - Is pulserx-worker active?
2. **Decide:** Free tier (no reminders) or Starter plan (full features)
3. **If paid:** Upgrade worker to Starter plan
4. **If free:** Document that reminders need paid tier

---

**Bottom Line:** Reminder notifications require an active Celery worker, which needs Render's Starter plan ($7/mo). Everything else works on free tier.
