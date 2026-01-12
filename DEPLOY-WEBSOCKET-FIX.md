# Deploy WebSocket Fix to Render

## Quick Deploy

Run these commands to deploy the WebSocket fix:

```bash
# Stage the changes
git add templates/base.html

# Commit with descriptive message
git commit -m "Fix WebSocket connection to use dynamic host for Render deployment

- Changed hardcoded 127.0.0.1:8000 to window.location.host in base.html
- Enables WebSocket connections to work on Render and any deployment
- Maintains backward compatibility with local development
- Fixes: Patient WebSocket closed error preventing dynamic messaging"

# Push to trigger Render deployment
git push origin main
```

## What Happens Next

1. **Render Auto-Deploy** (2-5 minutes)
   - Render detects the push
   - Runs build.sh
   - Restarts the web service with Daphne
   - WebSocket connections will now work

2. **Monitor Deployment**
   - Go to Render dashboard
   - Click on your PulseRx service
   - Watch the "Events" tab for deployment progress
   - Check "Logs" tab for any errors

## Post-Deployment Testing

### Step 1: Check WebSocket Connection

1. Open your Render app URL in browser
2. Open Developer Tools (F12) → Console tab
3. Login as any user
4. Look for: `"Connected to notification WS"`

**Expected:**
```
Connected to notification WS
```

**If you see errors instead:**
- Check [WEBSOCKET-TROUBLESHOOTING.md](WEBSOCKET-TROUBLESHOOTING.md)

### Step 2: Test Real-Time Messaging

#### Setup (Using Two Browser Contexts)

**Regular Browser Window:**
```
1. Go to your Render URL
2. Login as: ngeorge / pharmacist123
```

**Incognito Window:**
```
1. Go to your Render URL (same URL)
2. Login as: jjackson / patient123
```

#### Test Sequence

**In Patient Window (Incognito):**
1. Navigate to Messages
2. Find or create a conversation with the pharmacy
3. Send a message: "Hi, I need help with my prescription"

**In Pharmacist Window (Regular):**
1. Watch for notification badge to update (should be instant)
2. Click notification bell
3. Should see new message notification
4. Click to open message thread

**In Both Windows:**
1. Open the same message thread
2. Send messages back and forth
3. Messages should appear instantly without refresh
4. Type and send from either side
5. Other side should see it immediately

### Step 3: Test Notification System

**In Pharmacist Window:**
1. Send a system notification or message
2. Notification badge should update immediately

**In Patient Window:**
1. Should see notification badge update
2. Click notification bell
3. Should see new notification
4. Click notification
5. Should navigate to relevant page

## Verification Checklist

After deploying, verify these work:

- [ ] No console errors about WebSocket connections
- [ ] Console shows "Connected to notification WS"
- [ ] Console shows "Connected to message WebSocket" (when in thread)
- [ ] Notification badge updates in real-time
- [ ] Messages appear instantly in threads
- [ ] Multiple users can chat in real-time
- [ ] No page refresh needed for updates

## Common Issues After Deploy

### Issue 1: WebSocket Still Closes Immediately

**Symptoms:**
```
WebSocket closed: 1006
```

**Solutions:**
1. Check Render Redis is running (Dashboard → Redis instance)
2. Verify REDIS_URL environment variable is set
3. Check web service is using Daphne (not Gunicorn)
4. Review Render logs for errors

### Issue 2: Connection Times Out

**Symptoms:**
```
WebSocket error: [timeout]
```

**Solutions:**
1. Check Render service is running (not sleeping)
2. Verify no firewall blocking WebSocket
3. Check ALLOWED_HOSTS includes your Render domain
4. Verify CSRF_TRUSTED_ORIGINS includes your Render domain

### Issue 3: Mixed Content Errors

**Symptoms:**
```
Mixed Content: The page at 'https://...' was loaded over HTTPS, but attempted to connect to 'ws://...'
```

**Solutions:**
- This shouldn't happen with the fix (protocol auto-detection)
- If it does, verify the protocol line in base.html:
  ```javascript
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  ```

## Rollback Plan

If something goes wrong:

```bash
# Revert the commit
git revert HEAD

# Push the revert
git push origin main
```

Or restore manually:
```javascript
// In templates/base.html, line 448, change back to:
const socket = new WebSocket(`${protocol}://127.0.0.1:8000/ws/notifications/`);
```

## Additional Documentation

- **Full Fix Details**: [WEBSOCKET-FIX-SUMMARY.md](WEBSOCKET-FIX-SUMMARY.md)
- **Troubleshooting Guide**: [WEBSOCKET-TROUBLESHOOTING.md](WEBSOCKET-TROUBLESHOOTING.md)
- **Demo Testing**: [DEMO-QUICK-START.md](DEMO-QUICK-START.md)

## Support

If WebSocket still doesn't work after deploying:

1. **Check Render Logs**
   - Dashboard → Your Service → Logs
   - Look for WebSocket errors or Redis connection issues

2. **Check Browser Console**
   - F12 → Console tab
   - Copy error messages

3. **Check Network Tab**
   - F12 → Network tab → Filter: WS
   - Check WebSocket connection status and response

4. **Verify Environment**
   - Dashboard → Your Service → Environment
   - Ensure REDIS_URL is set
   - Ensure ALLOWED_HOSTS includes your domain

---

**Ready to deploy? Run the git commands at the top! 🚀**
