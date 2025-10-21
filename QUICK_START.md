# 📋 Deployment Checklist

## Pre-Deployment ✅

- [ ] Test bot locally with `/start` command
- [ ] Test all commands (`/help`, `/setformat`, `/setemoji`, etc.)
- [ ] Verify API server responds at `http://localhost:5000/api/health`
- [ ] Confirm `user_configs.json` is created and saves settings
- [ ] Check that Chrome extension can fetch config from API

## Quick Deployment Steps (Railway Recommended)

### Step 1: GitHub Setup (5 minutes)
```bash
# 1. Create GitHub account (free)
# 2. Create new repository: "Telebot"
# 3. Run these commands in your project folder:

git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/Telebot.git
git push -u origin main
```

### Step 2: Railway Deployment (3 minutes)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your "Telebot" repository
4. Wait for automatic deployment

### Step 3: Configure Bot Token (2 minutes)
1. In Railway dashboard, go to **Variables**
2. Add new variable:
   - **Key:** `TELEGRAM_BOT_TOKEN`
   - **Value:** Your token from @BotFather

### Step 4: Get Deployment URL (1 minute)
- Railway shows your public URL (something like: `https://telebot-production-xxxx.up.railway.app`)
- This is your API endpoint

### Step 5: Update Chrome Extension
- Change API URL from `http://localhost:5000` to your Railway URL
- Test by sending a message through Telegram

## **Total Time: ~15 minutes** ⚡

---

## What Gets Deployed

✅ **telebot.py** - Your bot with all commands
✅ **api_server.py** - REST API for Chrome extension  
✅ **user_configs.json** - Stores user settings
✅ **requirements.txt** - Dependencies
✅ **Procfile** - Tells Railway how to run your app

## After Deployment

### Test Endpoints

**Health Check:**
```
GET https://your-railway-url.up.railway.app/api/health
Response: {"status": "ok"}
```

**Get User Config:**
```
GET https://your-railway-url.up.railway.app/api/config/123456789
Response: {"success": true, "config": {"message_format": "now playing", "emoji": "🎵"}}
```

### Monitor Your Bot

1. **Check Logs:**
   - Railway dashboard → View logs
   - Look for errors or issues

2. **Test Commands:**
   - Open Telegram
   - Send `/start` to your bot
   - Send `/myconfig` to verify settings work
   - Send `/setformat` and verify it saves

3. **Test API:**
   - Visit `https://your-railway-url.up.railway.app/api/health`
   - Should return `{"status": "ok"}`

---

## Common Issues & Fixes

### "Bot not responding"
**Solution:**
1. Check Railway logs for errors
2. Verify `TELEGRAM_BOT_TOKEN` is set correctly
3. Restart the deployment

### "Chrome extension can't fetch config"
**Solution:**
1. Update API URL in extension to your Railway URL
2. Check CORS is enabled in `api_server.py` (it is)
3. Verify `/api/health` endpoint works

### "Port error"
**Solution:** Don't worry! Railway assigns PORT automatically. Our code handles it.

---

## File Structure After Deployment

```
Your Bot (Running on Railway)
├── telebot.py          ← Bot with /start, /help, /setformat, etc.
├── api_server.py       ← API for Chrome extension
├── user_configs.json   ← Auto-created, stores user settings
└── requirements.txt    ← Dependencies (auto-installed)
```

---

## Next Steps

1. **Deploy Now:** Follow steps above
2. **Share Your Bot:** Give bot username to friends
3. **Monitor:** Check logs occasionally
4. **Scale:** If needed, upgrade Railway plan

---

## Cost

- **Railway Free Tier:** $5/month credit (usually enough)
- **Upgrades:** Paid plans available if needed

---

## Support

- Railway Docs: https://docs.railway.app
- Telegram Bot API: https://core.telegram.org/bots/api
- Having issues? Check logs in Railway dashboard

---

**Status:** Ready for deployment! 🚀
