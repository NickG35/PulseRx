# Celery Worker Memory Issue - CRITICAL FIX

## The Real Problem

Your Celery worker keeps crashing with:
```
Instance failed: chrtx
Ran out of memory (used over 512MB) while running your code.
```

**Root Cause:** Render Free tier workers have a **512MB memory limit**, and your Celery worker is exceeding this.

## Why This Happens

Celery workers can consume significant memory, especially with:
- Django ORM loaded
- Multiple tasks
- Redis connections
- Long-running processes

Your worker is hitting the 512MB limit and crashing, which is why **reminders don't send**.

## Solutions

### Solution 1: Optimize Celery Worker Memory (Try This First)

Update your Celery worker start command to use memory-efficient settings:

**In render.yaml, change line 34:**

**From:**
```yaml
startCommand: "celery -A PulseRx worker --loglevel=info"
```

**To:**
```yaml
startCommand: "celery -A PulseRx worker --loglevel=warning --max-tasks-per-child=10 --pool=solo"
```

**What this does:**
- `--loglevel=warning` - Reduces log memory usage
- `--max-tasks-per-child=10` - Restarts worker after 10 tasks (prevents memory leaks)
- `--pool=solo` - Uses single-threaded pool (lower memory footprint)

**Pros:**
- ✅ Might work on free tier
- ✅ Still $0/month
- ✅ Worth trying first

**Cons:**
- ❌ Not guaranteed to stay under 512MB
- ❌ Slower task processing (single-threaded)

---

### Solution 2: Upgrade Worker to Starter Plan (Guaranteed Fix)

Render's Starter plan has **512MB-2GB memory** and won't crash.

**Cost:** $7/month

**In render.yaml, line 32:**
```yaml
- type: worker
  name: pulserx-worker
  runtime: python
  plan: starter  # Already set, just need to activate in dashboard
```

**Steps:**
1. Render Dashboard → pulserx-worker
2. Upgrade to Starter plan
3. Worker gets more memory
4. Reminders work reliably

**Pros:**
- ✅ Guaranteed to work
- ✅ Better performance
- ✅ Production-ready

**Cons:**
- ❌ Costs $7/month

---

### Solution 3: Remove Celery Worker (Stay Free)

Accept that reminders won't work on free deployment.

**Change render.yaml to:**
```yaml
services:
  - type: web
    name: pulserx
    # ... (keep web service)

  # REMOVE worker service entirely

  - type: redis
    name: pulserx-redis
    # ... (keep redis)
```

**Pros:**
- ✅ $0/month
- ✅ No memory crashes
- ✅ All other features work

**Cons:**
- ❌ No automated reminders

---

### Solution 4: Use Alternative Background Job Service

Use a different service for background tasks (e.g., Heroku Scheduler, cron-job.org).

**Not recommended** - adds complexity

---

## Recommended Immediate Fix

### Try Solution 1 First (Optimize Memory)

**Quick change:**

Edit render.yaml line 34:
```yaml
startCommand: "celery -A PulseRx worker --loglevel=warning --max-tasks-per-child=10 --pool=solo --concurrency=1"
```

Added `--concurrency=1` to further limit memory.

**Then deploy:**
```bash
git add render.yaml
git commit -m "Optimize Celery worker for memory constraints on free tier"
git push origin main
```

**Monitor in Render dashboard:**
- Check if worker stays alive
- Watch memory usage
- Test reminder creation

### If That Doesn't Work

**You have 2 choices:**
1. **Pay $7/mo** for Starter plan (reliable)
2. **Remove worker** and keep app free (no reminders)

---

## Updated render.yaml (Optimized for Free Tier)

```yaml
services:
  # Web Service (Daphne ASGI Server)
  - type: web
    name: pulserx
    runtime: python
    plan: free
    buildCommand: "./build.sh"
    startCommand: "daphne -b 0.0.0.0 -p $PORT PulseRx.asgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: pulserx-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: pulserx-redis
          property: connectionString

  # Celery Background Worker (OPTIMIZED FOR LOW MEMORY)
  - type: worker
    name: pulserx-worker
    runtime: python
    plan: free  # Try free first with optimizations
    buildCommand: "pip install -r requirements.txt"
    startCommand: "celery -A PulseRx worker --loglevel=warning --max-tasks-per-child=10 --pool=solo --concurrency=1 --without-gossip --without-mingle --without-heartbeat"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        sync: false
      - key: DEBUG
        value: False
      - key: DATABASE_URL
        fromDatabase:
          name: pulserx-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: pulserx-redis
          property: connectionString

  # Redis Instance
  - type: redis
    name: pulserx-redis
    plan: free
    maxmemoryPolicy: allkeys-lru
    ipAllowList: []

databases:
  - name: pulserx-db
    plan: free
    databaseName: pulserx
    user: pulserx
```

**Key optimizations added:**
- `--loglevel=warning` - Less logging = less memory
- `--max-tasks-per-child=10` - Restart after 10 tasks
- `--pool=solo` - Single process pool
- `--concurrency=1` - Only 1 worker at a time
- `--without-gossip` - Disable gossip protocol (saves memory)
- `--without-mingle` - Disable mingle (saves memory)
- `--without-heartbeat` - Disable heartbeat (saves memory)

---

## Testing After Fix

1. **Deploy optimized config:**
```bash
git add render.yaml
git commit -m "Optimize Celery worker memory usage for free tier

- Use solo pool instead of prefork
- Limit concurrency to 1 worker
- Disable gossip, mingle, heartbeat protocols
- Reduce logging to warning level
- Restart worker after 10 tasks to prevent memory leaks"
git push origin main
```

2. **Monitor Render Dashboard:**
   - pulserx-worker → Logs
   - Watch for "Ran out of memory" errors
   - If it stays alive, test creating a reminder

3. **Test reminder:**
   - Create reminder with time in 5 minutes
   - Watch worker logs for task execution
   - Check if notification appears

---

## If Optimizations Don't Work

**Your realistic options:**

1. **Upgrade to Starter ($7/mo)** - Most reliable
2. **Remove worker entirely** - Keep app free, no reminders
3. **Accept intermittent crashes** - Worker restarts but unreliable

For a portfolio project, **Option 2 (remove worker)** is totally acceptable. You can say:

> "The app includes scheduled reminders using Celery. Due to free tier memory constraints (512MB), the worker is disabled in production but fully functional locally. This demonstrates understanding of background task architecture."

---

## My Recommendation

**Try the memory optimizations** (Solution 1) first. If the worker still crashes:

**Remove the worker** and keep everything else free. Here's why:

✅ All your impressive features work (WebSocket, messaging, inventory)
✅ $0 cost
✅ No crashes
✅ Shows you understand the trade-offs
✅ Can mention "works locally with Celery" in demos

The WebSocket notifications (which we just fixed) are arguably more impressive than scheduled reminders anyway!

---

## Want me to apply the fix?

I can update render.yaml with the memory optimizations. Should I:
1. **Apply memory optimizations** and push?
2. **Remove worker entirely** for stability?
3. **Just explain** and let you decide?

Let me know!
