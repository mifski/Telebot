# YouTube to Telegram Bot 🎵

A Telegram bot that lets users automatically post YouTube videos they're watching to their Telegram channel with customizable messages and emojis.

## Features

- ✅ Customize message format (`/setformat`)
- ✅ Choose custom emoji (`/setemoji`)
- ✅ Preview messages before posting
- ✅ Get channel ID helper
- ✅ Per-user configuration storage
- ✅ Chrome extension integration

## Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Chrome extension installed

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Telebot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variable**
   ```bash
   set TELEGRAM_BOT_TOKEN=your_token_here  # Windows
   export TELEGRAM_BOT_TOKEN=your_token_here  # Mac/Linux
   ```

5. **Run both servers**
   ```bash
   # Terminal 1 - Bot
   python telebot.py

   # Terminal 2 - API
   python api_server.py
   ```

### Deploy to Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Push Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Create Railway Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your Telebot repository

4. **Add Environment Variables**
   - Go to Variables tab
   - Add: `TELEGRAM_BOT_TOKEN` = your_token_here

5. **Deploy**
   - Railway will automatically deploy when you push to GitHub

## Commands

- `/start` - Welcome message
- `/help` - Full guide
- `/setformat` - Change message format
- `/setemoji` - Choose emoji
- `/preview` - Preview your messages
- `/myconfig` - View your settings
- `/reset` - Reset to defaults
- `/getchannelid` - Get your channel ID
- `/support` - Get support

## API Endpoints

- `GET /api/config/{user_id}` - Get user configuration
- `GET /api/health` - Health check

## File Structure

```
Telebot/
├── telebot.py          # Main bot with commands
├── api_server.py       # Flask API for extension
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment configuration
├── .gitignore          # Git ignore rules
├── user_configs.json   # User settings (auto-created)
└── README.md           # This file
```

## Troubleshooting

### Bot not responding
- Check if `TELEGRAM_BOT_TOKEN` is set correctly
- Ensure bot is running (`python telebot.py`)
- Check logs for errors

### API server not working
- Make sure Flask is installed
- Check if port 5000 is available
- Run `python api_server.py`

## Support

For issues or questions, contact @YourUsername on Telegram

## License

MIT License
