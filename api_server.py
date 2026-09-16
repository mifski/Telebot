"""
API Server for the Chrome extension
Runs automatically inside telebot.py, or standalone: python api_server.py

The extension sends its connection code (from /connect) plus the video title and URL.
The server looks up whose code it is, formats the post with their /setformat and
/setemoji settings, and posts it to their channel.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from html import escape
import logging
import socket
import time
import requests
import storage
from config import BOT_TOKEN, HOST, IS_DEPLOYED, PORT

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow requests from Chrome extension

# Don't post the same video twice in a row within this many seconds (e.g. two tabs, two computers)
DUPLICATE_WINDOW_SECONDS = 10 * 60
_last_posts = {}  # user_id -> (url, time posted)

INVALID_CODE = "hmm, I don't recognise that code! send /connect to the bot and paste the new one in ( ˘ ³˘)♡"
NO_CHANNEL = "no channel yet! add the bot to your channel as an admin with \"Post Messages\" (or use /setchannel) 🌸"

# Friendlier explanations for the most common Telegram errors
ERROR_HINTS = {
    "chat not found": "I can't find that channel anymore — add the bot back as an admin 🥺",
    "not enough rights": "the bot can't post there yet — give it the \"Post Messages\" permission ♡",
    "need administrator rights": "the bot can't post there yet — give it the \"Post Messages\" permission ♡",
    "bot is not a member": "the bot isn't in your channel — add it as an admin!",
    "bot was kicked": "the bot was removed from your channel — add it back whenever you're ready ♡",
    "unauthorized": "the bot token isn't valid — check TELEGRAM_BOT_TOKEN (in .env locally, or your host's variables).",
}

def build_message(config, title, url):
    """Build the channel post as HTML, so titles containing [ ] _ * can't break it"""
    return (
        f"{escape(config['emoji'])} {escape(config['message_format'])}\n\n"
        f'<a href="{escape(url, quote=True)}">{escape(title)}</a>'
    )

def error_response(message, status):
    logger.warning(f"❌ {message}")
    return jsonify({"success": False, "error": message}), status

def user_from_request():
    """Returns (request data, user_id, settings) - user_id is None for an unknown code"""
    data = request.get_json(silent=True) or {}
    user_id, user = storage.find_user_by_code(str(data.get("code") or "").strip())
    return data, user_id, user

def post_to_telegram(chat_id, text):
    """Send a message; returns None on success or an error message"""
    try:
        result = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
            timeout=15
        ).json()
    except (requests.RequestException, ValueError) as e:
        # Don't include str(e) - it contains the request URL, which contains the bot token
        return f"couldn't reach Telegram just now ({type(e).__name__}) — maybe check the connection? (´•ω•̥`)"

    if result.get("ok"):
        return None
    description = result.get("description", "something unexpected")
    hint = next((h for key, h in ERROR_HINTS.items() if key in description.lower()), None)
    return f"{hint} (Telegram said: {description})" if hint else f"Telegram said: {description}"

@app.route('/api/me', methods=['POST'])
def me():
    """Tell the extension who it's connected as"""
    _, user_id, user = user_from_request()
    if not user_id:
        return error_response(INVALID_CODE, 401)
    return jsonify({
        "success": True,
        "channel": user.get("channel_title") if user.get("channel_id") else None,
        "paused": bool(user.get("paused")),
        "format": f"{user['emoji']} {user['message_format']}"
    })

@app.route('/api/send-video', methods=['POST'])
def send_video():
    """Receive video from extension and post to Telegram"""
    data, user_id, user = user_from_request()
    title = str(data.get('title') or '').strip()[:300]
    url = str(data.get('url') or '').strip()
    is_test = bool(data.get('test'))

    if not user_id:
        return error_response(INVALID_CODE, 401)
    if not title or not url.startswith(('https://', 'http://')):
        return error_response("that video's title or link looks off (・_・;)", 400)
    if not BOT_TOKEN:
        return error_response("the bot token isn't set up on the server 🥺", 500)
    if not user.get("channel_id"):
        return error_response(NO_CHANNEL, 400)

    if not is_test:
        if user.get("paused"):
            return jsonify({"success": False, "paused": True, "error": "posting is on pause — send /resume to the bot ♡"})
        last_url, last_time = _last_posts.get(user_id, (None, 0))
        if url == last_url and time.time() - last_time < DUPLICATE_WINDOW_SECONDS:
            return jsonify({"success": True, "skipped": True, "message": "already shared that one just now ♡"})

    error = post_to_telegram(user["channel_id"], build_message(user, title, url))
    if error:
        return error_response(error, 400)

    if not is_test:
        _last_posts[user_id] = (url, time.time())
    logger.info(f"♡ posted '{title}' for user {user_id}")
    return jsonify({"success": True, "message": "posted! ♡"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - hosts ping this to see we're alive"""
    return jsonify({"status": "ok"})

@app.route('/', methods=['GET'])
def home():
    """A friendly page for anyone who opens the server URL in a browser"""
    return (
        "<!doctype html><meta charset=utf-8>"
        "<title>YouTube to Telegram</title>"
        "<style>body{margin:0;min-height:100vh;display:grid;place-items:center;text-align:center;"
        "font-family:'Segoe UI Rounded','SF Pro Rounded',ui-rounded,-apple-system,'Segoe UI',sans-serif;"
        "color:#5b4a58;background:linear-gradient(160deg,#fff4f8,#f1f0ff)}"
        "div{background:#fff;padding:34px 40px;border-radius:24px;box-shadow:0 6px 24px rgba(142,110,140,.16)}"
        "h1{margin:0 0 6px;font-size:19px}p{margin:0;font-size:13px;color:#a08fa0}"
        "@media(prefers-color-scheme:dark){body{color:#f6eaf3;background:linear-gradient(160deg,#2a2333,#241f2e)}"
        "div{background:#332b3f}p{color:#b9a8c4}}</style>"
        "<div><h1>♡ I'm awake and listening ♡</h1>"
        "<p>your music is safe with me — talk to the bot on Telegram ✨</p></div>"
    )

def port_in_use():
    """On Windows two servers can bind the same port, and requests go to the old one"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", PORT)) == 0

def run():
    """Start the API server (waitress is a production-ready server that also works on Windows)"""
    from waitress import serve
    # Only worth checking on your own machine - on a host nothing else shares the port
    if not IS_DEPLOYED and port_in_use():
        logger.error(f"❌ Port {PORT} is already in use - an older telebot.py or api_server.py is probably still running. Close it and restart.")
        return
    logger.info(f"🚀 API Server running on http://{HOST}:{PORT}")
    serve(app, host=HOST, port=PORT)

if __name__ == "__main__":
    import sys
    # Windows consoles often use a non-UTF-8 codepage (e.g. GBK) and crash on emoji
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    run()
