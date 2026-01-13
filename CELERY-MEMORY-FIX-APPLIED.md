# Celery Worker Memory Fix - APPLIED

## The Issue

Your Celery worker on Render Starter plan was crashing with:
```
Instance failed: chrtx
Ran out of memory (used over 512MB)
```

Even though you're on **Starter plan** (which should have more memory), the default Celery configuration was using too much memory.

## The Fix Applied

Changed [render.yaml:34](render.yaml#L34) from:
```yaml
startCommand: "celery -A PulseRx worker --loglevel=info"
```

To:
```yaml
startCommand: "celery -A PulseRx worker --loglevel=warning --max-tasks-per-child=50 --pool=solo --concurrency=1 --without-gossip --without-mingle"
```

## What Each Flag Does

| Flag | Purpose | Memory Impact |
|------|---------|---------------|
| `--loglevel=warning` | Only log warnings/errors | ✅ Reduces log buffer memory |
| `--max-tasks-per-child=50` | Restart worker after 50 tasks | ✅ Prevents memory leaks from accumulating |
| `--pool=solo` | Use single-threaded execution pool | ✅ Lower memory footprint than prefork |
| `--concurrency=1` | Only 1 task executes at a time | ✅ Limits concurrent memory usage |
| `--without-gossip` | Disable cluster gossip protocol | ✅ Removes gossip communication overhead |
| `--without-mingle` | Disable worker startup synchronization | ✅ Removes mingle protocol overhead |

## Why This Should Work

**Before (Default Celery):**
- Prefork pool with multiple worker processes
- Full INFO logging (verbose)
- Gossip and mingle protocols active
- Workers never restart (memory leaks accumulate)
- **Result:** 500MB+ memory usage

**After (Optimized):**
- Solo pool (single process)
- Minimal WARNING logging
- No gossip/mingle overhead
- Workers restart every 50 tasks (clears leaks)
- **Expected:** 150-300MB memory usage

## Deploy the Fix

```bash
git add render.yaml
git commit -m "Optimize Celery worker to prevent memory crashes

- Use solo pool instead of prefork (lower memory)
- Limit concurrency to 1 worker
- Restart worker every 50 tasks to prevent leaks
- Disable gossip and mingle protocols
- Reduce logging to warning level
- Fixes: Worker memory crashes on Starter plan"
git push origin main
```

## Expected Results After Deploy

1. **Worker stays alive** - No more "Ran out of memory" crashes
2. **Reminders work** - Notifications send at scheduled times
3. **Stable performance** - Worker restarts periodically to prevent leaks

## Monitoring After Deploy

### 1. Check Worker Status (Render Dashboard)

**Go to:** Dashboard → pulserx-worker → Logs

**Look for:**
```
[2026-01-13 12:00:00] celery@pulserx-worker ready.
[2026-01-13 12:00:00] [tasks]
[2026-01-13 12:00:00]   . accounts.tasks.send_reminder
```

**Good sign:** Worker stays running, no crashes

**Bad sign:** Still seeing "Ran out of memory" errors

### 2. Test Reminder Notification

**Create a test reminder:**
1. Login as patient on Render
2. Create reminder with time in 5 minutes
3. Wait 5 minutes
4. Check if notification appears

**Watch worker logs for:**
```
[2026-01-13 12:05:00] Received task: accounts.tasks.send_reminder[abc-123]
[2026-01-13 12:05:00] Task accounts.tasks.send_reminder[abc-123] succeeded in 0.5s
```

### 3. Monitor Memory (Optional)

If you have access to Render metrics:
- Watch memory usage over time
- Should stay well below 512MB
- May see periodic dips when worker restarts (every 50 tasks)

## Trade-offs

### Pros ✅
- Much lower memory usage
- No more crashes
- Reminders work reliably
- Worker restarts prevent leaks

### Cons ⚠️
- Slower task processing (single task at a time)
- Less detailed logs (warning level only)
- No cluster features (gossip/mingle disabled)

**For your app:** These trade-offs are fine! You don't have massive task volumes, so single-threaded processing is perfectly adequate.

## If It Still Crashes

If the worker STILL runs out of memory after this fix:

### Debug Steps:

1. **Check worker logs** for what's consuming memory:
```
Look for:
- Large Django ORM queries
- Memory warnings
- Task execution times
```

2. **Check task code** in [accounts/tasks.py](accounts/tasks.py):
```python
# Current task is simple, shouldn't use much memory
@shared_task
def send_reminder(time_id):
    # ... creates 1 notification
    # ... sends 1 WebSocket message
```

3. **Possible culprits:**
   - Old tasks queued in Redis (unlikely)
   - Memory leak in Django ORM (unlikely with solo pool)
   - Render Starter plan actually on 512MB tier (check plan details)

### Nuclear Option:

If it keeps crashing, you could restart worker every 10 tasks instead:
```yaml
--max-tasks-per-child=10
```

But this shouldn't be necessary.

## Performance Impact

**Task throughput:**
- **Before:** Could handle ~10 concurrent tasks
- **After:** 1 task at a time (sequential)

**For your reminder volume:**
- You probably have <100 reminders total
- Each takes <1 second to execute
- Sequential processing is totally fine

**Example:** Even with 100 reminders all due at 9:00 AM:
- Sequential: 100 seconds = 1.5 minutes to process all
- Concurrent: Maybe 30 seconds

The difference is negligible for your use case.

## What Happens Now

After you push this fix:

1. **Render detects change** → Redeploys worker
2. **Worker starts with new command** → Lower memory usage
3. **Scheduled tasks execute** → Reminders send notifications
4. **Worker periodically restarts** → Clears any memory leaks
5. **Everything works!** 🎉

## Testing Checklist

After deploying:

- [ ] Worker shows as "Live" in Render dashboard
- [ ] No "Ran out of memory" errors in logs
- [ ] Worker logs show `celery@pulserx-worker ready`
- [ ] Create test reminder with time in 5 min
- [ ] Notification appears at scheduled time
- [ ] Worker logs show task succeeded
- [ ] No crashes over 24 hours

## Files Changed

- [render.yaml](render.yaml) - Line 34 (Celery start command)

## Ready to Deploy?

Run these commands:

```bash
git add render.yaml
git commit -m "Optimize Celery worker to prevent memory crashes"
git push origin main
```

Then monitor the worker in Render dashboard!

---

**This should fix your reminder notifications!** The memory optimization keeps the worker alive so it can actually execute the scheduled tasks. 🚀
