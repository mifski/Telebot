# Extension Testing Guide

## What You're Seeing in Console

The errors you mentioned are **NOT from our extension**:

- ❌ `about:blank sandboxed` - YouTube frame
- ❌ `403 Forbidden video fetch` - YouTube rate limiting 
- ❌ `requestStorageAccessFor denied` - YouTube storage access

## How to Test Our Extension

### Step 1: Reload Extension
1. Go to `chrome://extensions/`
2. Find "YouTube to Telegram"
3. Click the refresh icon (↻)
4. Wait 2 seconds

### Step 2: Configure Extension
1. Click extension icon (puzzle piece) → "YouTube to Telegram"
2. Enter:
   - **Channel ID**: `-1001234567890` (your actual channel ID)
   - **User ID**: `123456789` (your numeric user ID from @userinfobot)
3. Click "Save Configuration"
4. Click "Start Monitoring"

### Step 3: Open YouTube
1. Go to https://www.youtube.com/watch?v=dQw4w9WgXcQ
2. Let video play for a few seconds
3. **Look at the extension icon** - it should show "Active"

### Step 4: Check Extension Logs
1. Go to `chrome://extensions/`
2. Find "YouTube to Telegram"
3. Click "Service Worker" link under the extension name
4. This opens the background.js console
5. You should see logs like:
   - `Processing video: [video title]`
   - `✅ Video sent to Telegram`
   - **OR** `Config not set` if Channel/User ID missing

### Step 5: Check Bot Server Logs
1. Look at your terminal running `python api_server.py`
2. You should see:
   - `POST /api/send-video` request
   - `200 OK` response
   - Video title and URL

### Step 6: Verify in Telegram
1. Check your Telegram channel
2. Look for new message with format: `🎵 [Custom message]: [Title](URL)`

## Common Issues

**"Config not set"** in background.js
- Extension can't find saved Channel/User ID
- Solution: Fill in popup, click Save, restart monitoring

**No logs in Service Worker console**
- Service worker restarted and killed the console
- Solution: Reload extension and reproduce immediately

**Videos not posting**
1. Is bot server running? Check terminal for errors
2. Is bot admin in channel? Check bot permissions
3. Check User ID format (must be numeric from @userinfobot, not @username)

**"404 - Config not found"**
- User ID doesn't have a config in bot server
- Solution: Run `/myconfig` in bot first to create it

## Debug Mode

To enable verbose logging, update `background.js`:

```javascript
// Add near top of handleVideoUpdate function:
console.log("Config loaded:", config);
console.log("Full video data:", videoData);
```

Then reload extension and check Service Worker console again.

## Expected Flow

YouTube video plays → content.js detects → background.js gets config → API call to bot server → bot posts to channel

If any step fails, check logs at that step!
