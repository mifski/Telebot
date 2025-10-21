# Debugging: Why Videos Aren't Sending

## Step 1: Check Extension Configuration

1. Go to `chrome://extensions/`
2. Find "YouTube to Telegram" 
3. Click the extension icon
4. Verify:
   - ✅ Channel ID is filled in (should be `-1002568728245`)
   - ✅ User ID is filled in (numeric, from @userinfobot)
   - ✅ "Start Monitoring" button was clicked

## Step 2: Check Service Worker Logs

1. Go to `chrome://extensions/`
2. Find "YouTube to Telegram"
3. Click **"Service Worker"** link (under the extension name)
4. This opens the background script console
5. Look for ANY logs - you should see:
   - `Session started` when you click Start Monitoring
   - `Processing video: [title]` when a video plays
   - `✅ Video sent to Telegram` if it worked
   - OR `Error sending video:` if something failed

## Step 3: Check Content Script Console

1. Go to YouTube.com
2. Play any video
3. Open DevTools (F12)
4. Go to **Console** tab
5. Look for logs like:
   - `Video detected:` 
   - `Sending message to background:`
   - `Message sent, waiting for response`

## Step 4: Check API Server Logs

Look at the terminal running `python api_server.py`:
- Should show: `POST /api/send-video` request
- Should show: `Bot token found: 8315...`
- Should show: `✅ Message sent successfully` OR error

## Step 5: Check Bot Logs

Look at the terminal running `python telebot.py`:
- Should show: `🎵 Bot is running`
- Check for any error messages

## Common Issues & Fixes

### "Config not set" in Service Worker
- ❌ Extension popup didn't save config
- ✅ Fix: Fill in popup fields and click "Save Configuration"

### No logs appear in Service Worker
- ❌ Service worker crashed or restarted
- ✅ Fix: Reload extension and try again immediately

### "Error sending video: Failed to fetch"
- ❌ API server not running on port 5000
- ✅ Fix: Make sure `python api_server.py` is running in terminal

### API server shows no requests
- ❌ Extension not detecting videos
- ✅ Fix: Check content.js console for video detection logs

### Bot not posting to channel
- ❌ Bot not admin in channel
- ✅ Fix: Add bot as admin with "Post Messages" permission

## What Should Happen (Step by Step)

1. You play a YouTube video
2. Content script detects it: logs "Video detected:"
3. Content script sends message to background script
4. Background script receives message: logs "Processing video:"
5. Background script calls API server
6. API server logs "POST /api/send-video"
7. API server calls Telegram API with bot token
8. Bot posts message to your channel
9. You see message in Telegram! ✅

## Test Steps

1. **Open chrome://extensions/**
2. **Reload "YouTube to Telegram" extension**
3. **Click the extension icon and confirm config is saved**
4. **Click "Start Monitoring"**
5. **Open DevTools in YouTube (F12)**
6. **Go to Console tab**
7. **Play any YouTube video**
8. **Watch the logs appear in real-time**

Report what you see in each console!
