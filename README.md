# YouTube to Telegram ♡

A Telegram bot + Chrome extension that gently posts the YouTube videos you play to your
Telegram channel, in your own words and with your own little emoji.

```
🎵 now playing

Lofi Hip Hop Radio - Beats to Study/Relax to
```

## Features

- ☁️ **Runs in the cloud** — deploy once and your computer never has to be on ([DEPLOYMENT.md](DEPLOYMENT.md))
- 📦 The extension the bot sends you **already knows its address** — no URLs to type in
- ✅ Adding the bot to your channel as admin connects it automatically
- 🔗 The extension links to your account with a private code from `/connect` — no IDs to copy
- ✎ Custom message format (`/setformat`) and emoji (`/setemoji`), with `/preview`
- ⏸ `/pause` and `/resume` posting from your phone
- 🎧 Only posts videos you actually watch (10+ seconds, ads ignored), never the same one twice in a row
- ▶️ Works on YouTube, YouTube Shorts and YouTube Music
- 💌 A "send a test post" button that tells you exactly what's wrong, kindly

## Setup

### 1. Get the bot online

Get a token from [@BotFather](https://t.me/BotFather) (`/newbot`), then follow
**[DEPLOYMENT.md](DEPLOYMENT.md)** — about five minutes on Railway, and it stays up forever.

Prefer to run it on your own machine while you tinker? See
[Running it locally](QUICK_START.md#-running-it-locally-instead-for-development).
Posts only happen while that terminal is open.

### 2. Connect your channel

1. Send `/start` to your bot in Telegram (so it's allowed to message you)
2. Add the bot to your channel as an **admin** with **"Post Messages"**
3. The bot messages you: "✨ yay, channel connected!"

(Already added it earlier? Use `/setchannel @yourchannel` or `/setchannel -100...`.)

### 3. Install the extension

1. Send `/downloadextension` to the bot — the zip it sends is built for *your* server
2. Extract it, open `chrome://extensions/`, turn on **Developer mode**
3. Click **Load unpacked** and pick the folder
4. Send `/connect`, copy the code, paste it into the popup, press **save & connect**
5. Press **send a test post** — it should appear in your channel
6. Press **start listening** and play something ♬

## Commands

| Command | What it does |
|---|---|
| `/connect` | Your secret code for the extension |
| `/newcode` | A fresh code (the old one retires) |
| `/setchannel` | Connect a channel by hand |
| `/setformat` | The words before the title (e.g. "now playing") |
| `/setemoji` | Your little emoji |
| `/preview` | Peek at how posts will look |
| `/pause` / `/resume` | Quiet / listening again |
| `/myconfig` | Your current setup |
| `/reset` | Back to the cosy defaults |
| `/downloadextension`, `/installextension` | Get and install the extension |
| `/getchannelid`, `/help`, `/support` | Help |

## How it works

```
YouTube tab (content.js)  → notices a video you've watched for 10s
extension (background.js) → POST /api/send-video {code, title, url}
api_server.py             → looks up whose code it is, formats the post
Telegram                  → the post appears in that user's channel
```

Settings live in `user_configs.json` (set `DATA_DIR` to keep it on a persistent volume).

## Project layout

| Path | What it is |
|---|---|
| `telebot.py` | The bot. Starts the API server too, so one process runs everything |
| `api_server.py` | The endpoint the extension talks to |
| `storage.py` | Everyone's settings, shared by both |
| `config.py` | Environment variables, including auto-detecting the public URL |
| `build_extension.py` | Zips `extension/` with the server's address baked in |
| `extension/` | The Chrome extension source |
| `chrome_extension.zip` | A prebuilt copy (rebuild: `python build_extension.py`) |

## API Endpoints

- `POST /api/send-video` — `{code, title, url}` → posts to the code owner's channel
- `POST /api/me` — `{code}` → which channel the code posts to
- `GET /api/health` — health check
- `GET /` — a friendly "I'm awake" page

## Troubleshooting

Press **send a test post** in the extension first — it tells you what's wrong:

| Message | Fix |
|---|---|
| can't reach the bot at… | Server asleep or wrong URL — open the URL in a browser to check |
| I don't recognise that code | Send `/connect` and paste the code again |
| no channel yet | Add the bot to your channel as admin with "Post Messages" |
| the bot can't post there yet | Give it the "Post Messages" admin permission |
| posting is on pause | Send `/resume` |

Test post works but videos don't post?
- Did you press **start listening**?
- Refresh YouTube tabs that were open before you installed/reloaded the extension
- Videos post after 10 seconds of playtime, not immediately
- Logs: `chrome://extensions` → YouTube to Telegram → **Service worker**

The bot ignores every command? Two copies are running with the same token — stop the one
on your computer.

## Support

Telegram: @physki · Email: izzychee1011@gmail.com

## License

MIT License
