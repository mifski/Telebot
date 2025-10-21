# YouTube to Telegram Bot - Setup Guide

## Step 1: Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/start` command
3. Send `/newbot` command
4. Follow the prompts to create a new bot
5. Copy your **bot token** (looks like: `1234567890:ABCDefGhIjKlMnOpQrStUvWxYz`)

## Step 2: Set Up Environment Variable

### Option A: Windows (Permanent - Recommended)
1. Right-click "This PC" → Properties
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: `TELEGRAM_BOT_TOKEN`
6. Variable value: `your_bot_token_here` (paste your token)
7. Click OK and restart terminal/VS Code
8. Restart the API server

### Option B: Create .env File (Easier for Testing)
1. In `d:\Telebot\`, create a file named `.env` (not .env.txt!)
2. Add this line:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
3. Save and restart the API server

### Option C: Set in Terminal (Temporary)
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
python api_server.py
```

## Step 3: Verify Bot Token is Loaded

1. Start the API server: `python api_server.py`
2. Check logs - you should see: `Bot token found: 1234567890...`
3. If you see "Bot token not configured!", go back to Step 2

## Step 4: Configure Extension

1. Go to `chrome://extensions/`
2. Reload the "YouTube to Telegram" extension
3. Click the extension icon
4. Enter your:
   - **Channel ID**: Your Telegram channel ID (starts with `-100`)
   - **User ID**: Your numeric ID (get from @userinfobot in Telegram)
5. Click "Save Configuration"

## Step 5: Test

1. Click "Start Monitoring"
2. Go to YouTube and play any video
3. Wait 3 seconds
4. Check your Telegram channel - should see the video message!

## Troubleshooting

**"Error sending video: Failed to fetch"**
- ❌ Bot token not set (fix: Set TELEGRAM_BOT_TOKEN)
- ❌ Bot server not running (fix: Run `python api_server.py`)
- ❌ Channel ID is wrong (fix: Check with `/getchannelid`)

**"Config not found" in Service Worker**
- ❌ User ID doesn't have config saved
- ✅ Fix: Run `/myconfig` in bot first

**Bot doesn't post to channel**
- ❌ Bot not admin in channel
- ✅ Fix: Add bot as admin with "Post Messages" permission
- ❌ Channel ID format wrong
- ✅ Fix: Use numeric ID like `-1001234567890`, not @channel_name

## Getting Your IDs

**Channel ID:**
- Telegram Desktop: Right-click channel → Copy link → ID is in URL
- OR use bot command: `/getchannelid`

**User ID:**
- Telegram: Search for @userinfobot
- Send any message
- It replies with your numeric user ID

**Bot Token:**
- Talk to @BotFather
- Use `/token` command if you forgot it

---

Once you set up the bot token, restart `api_server.py` and test the extension!
