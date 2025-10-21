# 🚀 Deployment Guide

Choose one of these free deployment options:

## Option 1: Railway (Recommended - Easiest) ⭐

### Step 1: Prepare Your Code
1. Create a GitHub account at https://github.com
2. Create a new repository named "Telebot"
3. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/Telebot.git
   git push -u origin main
   ```

### Step 2: Deploy on Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Search for "Telebot" repository
5. Click "Deploy"

### Step 3: Configure Environment Variables
1. In Railway dashboard, go to "Variables"
2. Add new variable:
   - **Key:** `TELEGRAM_BOT_TOKEN`
   - **Value:** Your bot token from @BotFather
3. Add another variable:
   - **Key:** `ENVIRONMENT`
   - **Value:** `production`

### Step 4: Get Your URLs
- Railway assigns a public URL to your app
- Your API will be at: `https://your-railway-url.up.railway.app/api/config/{user_id}`
- Update your Chrome extension to use this URL

---

## Option 2: Heroku (Free Tier Discontinued - Not Recommended)

Heroku no longer offers free tier. Use Railway instead.

---

## Option 3: PythonAnywhere (Easy for Beginners)

### Step 1: Create Account
1. Go to https://www.pythonanywhere.com
2. Sign up (free account available)

### Step 2: Upload Files
1. Go to "Files" tab
2. Upload all files from your Telebot folder

### Step 3: Create Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose Flask
4. Set the path to your `api_server.py`

### Step 4: Set Environment Variables
1. Edit `api_server.py`
2. Add at the top:
   ```python
   import os
   os.environ['TELEGRAM_BOT_TOKEN'] = 'your_token_here'
   ```

### Step 5: Create Console Task for Bot
1. Go to "Tasks" tab
2. Create new scheduled task
3. Command: `python /path/to/telebot.py`
4. Frequency: Run every hour (keeps it alive)

---

## Option 4: AWS (Free Tier for 12 Months)

### Using AWS Lambda (Serverless)

1. Create AWS account at https://aws.amazon.com/free
2. Go to Lambda service
3. Create function:
   - Runtime: Python 3.11
   - Upload code as ZIP

4. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your token

5. Configure API Gateway for Flask API

---

## Option 5: Google Cloud Run (Free Tier Available)

### Step 1: Prepare Dockerfile
Create a `Dockerfile` in your project:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=api_server.py
ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}

CMD exec gunicorn --bind :$PORT --workers 1 api_server:app & python telebot.py
```

### Step 2: Deploy
```bash
gcloud run deploy telebot --source .
```

---

## Recommended Option: Railway ✅

**Why Railway?**
- ✅ Easiest setup
- ✅ Free tier available
- ✅ GitHub integration
- ✅ Environment variables simple
- ✅ Good for beginners
- ✅ Automatic redeployment on code push

**Total Setup Time:** ~5 minutes

---

## After Deployment

### Update Chrome Extension
1. Open your extension settings
2. Change API URL from `http://localhost:5000` to your deployed URL:
   - Railway: `https://your-railway-url.up.railway.app`
   - PythonAnywhere: `https://yourusername.pythonanywhere.com`
   - Google Cloud Run: `https://telebot-xxxxx.run.app`

### Test Your Bot
1. Find your bot on Telegram
2. Send `/start`
3. Try `/help` to see all commands
4. Test `/setformat` and `/setemoji`

### Monitor Your Bot
- Check server logs for errors
- Monitor resource usage
- Keep bot token secret!

---

## Important Notes

⚠️ **Security:**
- Never commit your `TELEGRAM_BOT_TOKEN` to GitHub
- Always use environment variables
- Keep your token secret!

⚠️ **Rate Limits:**
- Telegram allows ~30 messages per second
- Add rate limiting for production

⚠️ **Uptime:**
- Free tiers may have limited uptime
- Consider paid tier for production

---

## Troubleshooting Deployment

### "ModuleNotFoundError"
- Make sure `requirements.txt` is in root directory
- Deployment should auto-install from it

### "Bot not responding"
- Check if `TELEGRAM_BOT_TOKEN` environment variable is set
- Check server logs for errors
- Restart the deployment

### "API 404 Not Found"
- Check your API URL is correct
- Make sure `api_server.py` is deployed
- Check CORS settings in Flask

### "Port already in use"
- Most platforms assign PORT via environment variable
- Our code handles this automatically

---

**Need Help?**
- Railway Docs: https://docs.railway.app
- PythonAnywhere Docs: https://www.pythonanywhere.com/help/
- Google Cloud Run: https://cloud.google.com/run/docs
