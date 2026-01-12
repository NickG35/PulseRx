# WebSocket Troubleshooting Guide

## Issue Fixed: Hardcoded WebSocket URL

### Problem
The WebSocket connection in [base.html:448](templates/base.html#L448) was hardcoded to `127.0.0.1:8000`, which prevented WebSocket connections from working on Render (or any deployment).

### Solution Applied
Changed from:
```javascript
const socket = new WebSocket(`${protocol}://127.0.0.1:8000/ws/notifications/`);
```

To:
```javascript
const socket = new WebSocket(`${protocol}://${window.location.host}/ws/notifications/`);
```

This allows the WebSocket to connect to the current host automatically, whether it's:
- `localhost:8000` (development)
- `your-app.onrender.com` (production)
- Any other domain

## Checking WebSocket Connection Status

### Browser Console
Open your browser's Developer Tools (F12) and check the Console tab:

**Successful Connection:**
```
Connected to notification WS
Connected to message WebSocket
```

**Connection Errors:**
```
WebSocket error: [error details]
WebSocket closed: [code] [reason]
```

### Common WebSocket Close Codes
- **1000**: Normal closure
- **1006**: Abnormal closure (connection lost without close frame)
- **1008**: Policy violation
- **1011**: Server error

## Testing on Render

### 1. Deploy the Fix
```bash
git add templates/base.html
git commit -m "Fix WebSocket URL to use dynamic host instead of hardcoded localhost"
git push origin main
```

Render will automatically redeploy.

### 2. Check WebSocket Connection

Open browser console on your Render app and look for:
- ✅ "Connected to notification WS"
- ✅ WebSocket connection in Network tab (filter by WS)

### 3. Test Real-time Features

**Test 1: Notifications**
1. Open two browser sessions (regular + incognito)
2. Login as Patient in one, Pharmacist in other
3. Send a message from Patient
4. Check if Pharmacist receives notification instantly

**Test 2: Messaging**
1. Patient and Pharmacist both open same message thread
2. Send messages back and forth
3. Messages should appear instantly without refresh

## Troubleshooting

### WebSocket Connection Fails (1006 Error)

**Possible Causes:**
1. **Redis not running** - Check Render Redis instance is active
2. **Daphne not running** - Ensure start command uses Daphne, not Gunicorn
3. **ASGI configuration issue** - Check [PulseRx/asgi.py](PulseRx/asgi.py)

**Check Redis:**
```bash
# In Render shell
echo $REDIS_URL
# Should output redis://...
```

**Check Start Command:**
```bash
# Should be:
daphne -b 0.0.0.0 -p $PORT PulseRx.asgi:application

# NOT:
gunicorn PulseRx.wsgi:application
```

### WebSocket Connects But No Messages

**Check Channel Layers Configuration:**

In [settings.py](PulseRx/settings.py), verify:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],  # Should use REDIS_URL env variable
        },
    },
}
```

### Mixed Content Errors (HTTP/HTTPS)

If you see mixed content warnings:
- Ensure `protocol` detection works: `window.location.protocol === "https:" ? "wss" : "ws"`
- On Render, this should automatically use `wss://` (WebSocket Secure)

### WebSocket Closes Immediately

**Check Authentication:**
- WebSocket consumers require authenticated users
- In [consumers.py:20-22](accounts/consumers.py#L20-L22), anonymous users are rejected
- Ensure user is logged in before WebSocket connects

## Debugging Commands

### Check Render Logs
```bash
# In Render dashboard
Navigate to: Your Service → Logs
```

Look for:
- WebSocket connection attempts
- Redis connection errors
- Channel layer errors
- Consumer errors

### Browser Network Tab
1. Open DevTools → Network tab
2. Filter by "WS" (WebSocket)
3. Click on the WebSocket connection
4. View:
   - **Headers**: Connection info
   - **Messages**: Data being sent/received
   - **Timing**: Connection duration

### Test WebSocket Manually

In browser console:
```javascript
// Test notification WebSocket
const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const testSocket = new WebSocket(`${protocol}://${window.location.host}/ws/notifications/`);

testSocket.onopen = () => console.log("✅ WebSocket connected");
testSocket.onerror = (e) => console.error("❌ WebSocket error:", e);
testSocket.onclose = (e) => console.log("⚠️ WebSocket closed:", e.code, e.reason);
```

## Environment Variables to Check on Render

Ensure these are set in Render dashboard:

```env
REDIS_URL=<internal-redis-url>
SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
```

## Files to Review

- [templates/base.html](templates/base.html) - Main notification WebSocket
- [accounts/templates/threads.html](accounts/templates/threads.html) - Message WebSocket
- [accounts/consumers.py](accounts/consumers.py) - WebSocket consumers
- [accounts/routing.py](accounts/routing.py) - WebSocket URL routing
- [PulseRx/asgi.py](PulseRx/asgi.py) - ASGI application config
- [PulseRx/settings.py](PulseRx/settings.py) - Channel layers config

## Expected Behavior After Fix

### On Render (Production)
- ✅ WebSocket connects via `wss://your-app.onrender.com`
- ✅ Real-time notifications work
- ✅ Real-time messaging works
- ✅ No console errors

### On Localhost (Development)
- ✅ WebSocket connects via `ws://localhost:8000`
- ✅ Everything works as before
- ✅ No changes needed for local development

## Quick Test Checklist

After deploying the fix:

- [ ] Open Render app in browser
- [ ] Open browser console (F12)
- [ ] Verify "Connected to notification WS" message
- [ ] Login as patient in regular tab
- [ ] Login as pharmacist in incognito tab
- [ ] Send message from patient
- [ ] Check if pharmacist receives notification instantly
- [ ] Open message thread on both sides
- [ ] Send messages back and forth
- [ ] Verify messages appear without page refresh

---

## Need More Help?

If WebSocket still doesn't work after this fix:
1. Check Render logs for errors
2. Verify Redis instance is running
3. Confirm Daphne is the start command
4. Check browser console for specific error messages
5. Review the files listed above for any other hardcoded URLs
