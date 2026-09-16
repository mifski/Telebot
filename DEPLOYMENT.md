# 🚀 Put the bot online (so you never run it locally)

Right now `python telebot.py` only works while your computer is on. Deploy it once and
it runs 24/7 — your computer can be closed, asleep, or on the other side of the world,
and your videos still get posted.

Everything runs in **one process** (`python telebot.py` starts both the bot and the
extension API), so any host that runs a long-lived Python process works.

**One rule:** only one copy of the bot may run at a time. Once it's deployed, stop the one
on your computer — otherwise Telegram returns "Conflict: terminated by other getUpdates request".

---

## Railway (recommended, ~5 minutes)

### 1. Push your code to GitHub
```bash
git add . && git commit -m "Ready to deploy" && git push
```
`.env`, `user_configs.json` and `channels_notified.json` are in `.gitignore`, so your
token and everyone's codes stay off GitHub.

### 2. Create the project
Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** →
pick this repository. Railway reads the `Procfile` (`web: python telebot.py`) and starts it.

### 3. Add a volume (do this before anyone connects!)
Settings → **Volumes** → mount a volume at `/data`.

Without it, `user_configs.json` is wiped on every deploy and everybody has to reconnect
from scratch. This is the step people skip and regret.

### 4. Set variables (Variables tab)

| Key | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | your token from @BotFather |
| `DATA_DIR` | `/data` |

### 5. Generate a public URL
Settings → Networking → **Generate Domain**.

You'll get something like `https://telebot-production-a1b2.up.railway.app`.
Open it in a browser — you should see a soft pink "I'm awake and listening" page.
(`/api/health` returns `{"status": "ok"}` if you prefer JSON.)

You do **not** need to set `PUBLIC_URL` — Railway tells the bot its own domain
automatically, and the bot bakes that address into every extension it hands out.

### 6. Stop your local copy
Close the terminal running `python telebot.py` on your computer. Done — it's live.

### 7. Get the extension again
In Telegram, send **/downloadextension**. The bot builds a fresh zip that already points
at your Railway URL, so there is nothing to type in. Install it
(see /installextension), paste your /connect code, and you're finished.

> Already had the old extension installed? Reinstall it from the new zip, or open the
> popup → **advanced** → paste your Railway URL → **save & connect**.

---

## Other hosts

Any always-on VPS, Raspberry Pi, or old laptop works too:

```bash
pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=... PORT=8080 PUBLIC_URL=https://your-domain.example python telebot.py
```

- **Render** — works the same way; `RENDER_EXTERNAL_URL` is picked up automatically.
  Avoid the free web tier: it sleeps when idle, and a sleeping bot posts nothing.
- **Fly.io** — `FLY_APP_NAME` is picked up automatically. Attach a volume for `DATA_DIR`.
- **Your own VPS** — set `PUBLIC_URL` yourself and put it behind HTTPS (Caddy or nginx).
  The extension can only talk to `https://` addresses, or `localhost` for testing.

**Won't work:** anything that sleeps when idle or runs briefly on request — free web tiers,
AWS Lambda, Cloud Run. The bot has to stay connected to Telegram to hear your commands.

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | **Required.** Your token from @BotFather |
| `DATA_DIR` | project folder | Where settings live. Point at a volume (e.g. `/data`) when deployed |
| `PUBLIC_URL` | auto-detected, else `http://localhost:5000` | The address baked into the extension |
| `PORT` | `5000` | Port the extension API listens on (hosts set this for you) |
| `HOST` | `127.0.0.1` locally, `0.0.0.0` when `PORT` is set | Interface to listen on |

`PUBLIC_URL` is detected from `RAILWAY_PUBLIC_DOMAIN`, `RENDER_EXTERNAL_URL` or
`FLY_APP_NAME` when you don't set it. Set it by hand on any other host.

---

## If something's off

| What you see | What's happening |
|---|---|
| Bot ignores every command | Two copies are running. Stop the local one. |
| "can't reach the bot at …" in the popup | Wrong URL, or the host is asleep. Open the URL in a browser to check. |
| Everyone had to reconnect after a deploy | No volume mounted, or `DATA_DIR` isn't set to it. |
| Extension worked locally, not deployed | It's an old zip with `localhost` inside. Send /downloadextension again. |

---

## Security notes

- Never commit your bot token — `.env` locally, host variables when deployed
- Each user's extension authenticates with their `/connect` code; `/newcode` revokes a leaked one
- A channel can only be connected by one of its admins (by adding the bot, or via `/setchannel`, which checks)
- The extension requests `https://*/*` so it can reach whatever host you deploy to; it only
  ever contacts the one URL configured in its popup
