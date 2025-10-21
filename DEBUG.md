# 🔧 Debugging Guide - Videos Not Sending

## Step 1: Check Bot Server is Running

```bash
# Terminal 1 - Start bot server with logging
cd d:\Telebot
set TELEGRAM_BOT_TOKEN=your_token_here
python api_server.py
```

**Expected output:**
```
🚀 API Server running on http://0.0.0.0:5000
```

If you see errors, check your bot token is set correctly.

---

## Step 2: Check Browser Console (Extension)

1. Open Chrome
2. Go to `chrome://extensions/`
3. Find "YouTube to Telegram" extension
4. Click **"Details"**
5. Click **"Inspect views background page"** or **"Inspect views popup"**
6. Open **Console** tab
7. Play a YouTube video

**Look for these logs:**

✅ Good:
```
🎵 YouTube to Telegram: Content script loaded!
🎵 Starting monitoring...
🎵 New video detected: [Video Title]
Sending video to bot server: {...}
Bot server response: {"success": true, ...}
✅ Video posted successfully!
```

❌ Bad:
```
Error: Failed to fetch
Could not fetch custom format
```

---

## Step 3: Check if Extension Calls Bot Server

**In browser console, should see:**
```
Bot server response: {...}
```

If you see "Error: Failed to fetch", the extension can't reach the bot server.

**Solutions:**
1. Check bot server URL in `background.js` matches your server
2. For local: should be `http://localhost:5000`
3. For production: should be your Railway URL
4. Make sure bot server is actually running

---

## Step 4: Check Bot Server Logs

**When playing a video, you should see in Terminal 1:**

```
2025-10-21 08:22:45 - DEBUG - Received request to /api/send-video
2025-10-21 08:22:45 - INFO - Processing video for user 123456789 to channel -100256872824...
2025-10-21 08:22:45 - DEBUG - Sending to Telegram: https://api.telegram.org/bot8315788328:AAG.../sendMessage
2025-10-21 08:22:46 - DEBUG - Telegram response: {'ok': True, ...}
2025-10-21 08:22:46 - INFO - ✅ Message sent successfully to -100256872824...
```

If you don't see this, extension isn't calling the API.

---

## Step 5: Verify Configuration

1. Open extension popup
2. Check values are saved:
   - Channel ID: `-100256872824...`
   - User ID: `123456789` (numeric!)
3. Click "Start Monitoring"
4. Play YouTube video

**If error:** "Please save your configuration first"
- Make sure both fields are filled
- Both must be numeric/valid format
- Save again

---

## Common Issues & Solutions

### Issue 1: "Failed to fetch"
```
Error: Failed to fetch
URL: http://localhost:5000/api/send-video
```

**Causes:**
- ❌ Bot server not running
- ❌ Wrong API URL in background.js
- ❌ Firewall blocking connection
- ❌ Network/CORS issue

**Fix:**
1. Check bot server is running: `python api_server.py`
2. Check URL in background.js matches server URL
3. Try accessing `http://localhost:5000/api/health` in browser
4. Should see: `{"status": "ok"}`

---

### Issue 2: "Bot token not configured"
```json
{
  "success": false,
  "error": "Bot token not configured on server"
}
```

**Causes:**
- ❌ TELEGRAM_BOT_TOKEN environment variable not set
- ❌ Bot server restarted after setting token

**Fix:**
```bash
set TELEGRAM_BOT_TOKEN=your_token_here
python api_server.py
```

Verify in terminal output:
```
Bot token found: 8315788328...
```

---

### Issue 3: Telegram error - "Bad Request"
```json
{
  "success": false,
  "error": "Bad Request: chat not found"
}
```

**Causes:**
- ❌ Wrong channel ID
- ❌ Bot not added as admin to channel
- ❌ Channel ID format incorrect

**Fix:**
1. Get channel ID: Send `/getchannelid` to bot
2. Copy the full ID (should start with `-100`)
3. Make sure bot is admin in channel with "Post Messages" permission
4. Enter exact ID in extension

---

### Issue 4: Message not appearing in channel
**But extension shows "success": true**

**Causes:**
- ❌ Wrong channel
- ❌ Bot was removed from channel
- ❌ Message deleted automatically
- ❌ Wrong channel ID saved

**Fix:**
1. Re-verify channel ID with `/getchannelid`
2. Check bot is still admin
3. Manually test: Send `/help` command in bot, should work
4. Check you're looking in correct channel

---

### Issue 5: User ID wrong
```
User ID entered: @physki (WRONG!)
```

**Causes:**
- ❌ Using username instead of numeric ID
- ❌ Didn't get ID from @userinfobot

**Fix:**
1. Open Telegram
2. Find `@userinfobot` 
3. Send it any message
4. It will reply with your numeric ID
5. Copy the NUMBER (e.g., `123456789`)
6. Paste in extension User ID field

---

## Testing Checklist

- [ ] Bot server running: `python api_server.py`
- [ ] `TELEGRAM_BOT_TOKEN` environment variable set
- [ ] Extension reloaded from `chrome://extensions`
- [ ] Channel ID correct (from `/getchannelid`)
- [ ] User ID numeric (from `@userinfobot`)
- [ ] Config saved in extension
- [ ] Monitoring started
- [ ] Opened YouTube tab
- [ ] Playing a video
- [ ] Check browser console for logs
- [ ] Check bot server terminal for logs

---

## Advanced Debugging

### Check API Health
```bash
# In another terminal
curl http://localhost:5000/api/health
```

Expected:
```json
{"status": "ok"}
```

### Test API Manually
```bash
curl -X POST http://localhost:5000/api/send-video \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "-100256872824",
    "user_id": "123456789",
    "message": "🎵 Test message: [Video](https://youtube.com)"
  }'
```

Should return:
```json
{"success": true, "message": "Video posted successfully"}
```

---

## Getting Help

When reporting issues, include:

1. **Bot server logs** (from Terminal 1)
   ```
   2025-10-21 08:22:45 - DEBUG - Received request...
   ```

2. **Browser console logs** (from DevTools)
   ```
   🎵 New video detected: Video Title
   Bot server response: {...}
   ```

3. **Your configuration:**
   - Channel ID: `-100...`
   - User ID: `123456...` (numeric)
   - Bot server URL: `http://localhost:5000`

4. **Error message** (exact text)

---

## Quick Fix Checklist

If videos not sending, try this order:

1. ✅ Restart bot server
2. ✅ Set TELEGRAM_BOT_TOKEN again
3. ✅ Reload extension
4. ✅ Check browser console
5. ✅ Check bot server terminal
6. ✅ Verify channel ID with `/getchannelid`
7. ✅ Verify User ID with `@userinfobot`
8. ✅ Test API manually with curl
9. ✅ Check bot is admin in channel

