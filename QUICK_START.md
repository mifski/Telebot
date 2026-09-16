# 📋 Quick Start Checklist

## ♡ The easy way: put it online once, forget about it

- [ ] Followed [DEPLOYMENT.md](DEPLOYMENT.md) (Railway, ~5 min)
- [ ] Mounted a volume and set `DATA_DIR` to it
- [ ] Opened your public URL — it shows "I'm awake and listening"
- [ ] Stopped any copy still running on your computer

Then set yourself up in Telegram:

- [ ] Sent `/start` to the bot
- [ ] Added the bot to your channel as admin with "Post Messages"
- [ ] Bot messaged you "yay, channel connected!" (or use `/setchannel @yourchannel`)
- [ ] `/connect` → copied the code
- [ ] `/downloadextension` → installed it (see `/installextension`)
- [ ] Pasted the code → **save & connect** shows "♡ posting to *your channel*"
- [ ] **send a test post** → it appears in the channel
- [ ] **start listening** → play a video for 10+ seconds → it appears too

The extension already knows your server's address — there's no URL to type in.

## 🛠 Running it locally instead (for development)

- [ ] `.env` contains `TELEGRAM_BOT_TOKEN=...` (from @BotFather)
- [ ] `pip install -r requirements.txt` (or run `setup.bat`)
- [ ] `python telebot.py` shows `♡ bot is awake and listening!`
- [ ] http://localhost:5000/api/health shows `{"status": "ok"}`
- [ ] Posts only happen while that terminal stays open

## 🎀 Customize

- [ ] `/setformat` and `/setemoji`
- [ ] `/preview` looks right
- [ ] `/pause` stops posts, `/resume` starts them again

## 🧩 After changing the extension code

The extension source lives in `extension/`. The bot zips it up on demand with your
server's address baked in, so:

1. Edit files in `extension/`
2. Send `/downloadextension` again (nothing to rebuild — it's built per request)
3. Click the refresh icon on the extension in `chrome://extensions`
4. Refresh open YouTube tabs

To rebuild the committed `chrome_extension.zip` by hand: `python build_extension.py`
