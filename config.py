"""
Settings loaded from environment variables / the .env file
"""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Bot Token - set TELEGRAM_BOT_TOKEN in .env or as an environment variable. Don't hardcode it here!
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# API Configuration - hosts like Railway set PORT; locally we only listen on this computer
PORT = int(os.getenv("PORT", 5000))
IS_DEPLOYED = bool(os.getenv("PORT"))
HOST = os.getenv("HOST") or ("0.0.0.0" if IS_DEPLOYED else "127.0.0.1")

# Where user settings are stored - point this at a persistent volume when deployed
DATA_DIR = os.getenv("DATA_DIR", BASE_DIR)


def _detect_public_url():
    """The address the Chrome extension should talk to.

    Set PUBLIC_URL yourself, or let it be picked up from the host's own variables.
    Falls back to localhost, which is right when you're running this on your computer.
    """
    explicit = os.getenv("PUBLIC_URL")
    if explicit:
        return explicit.rstrip("/")

    # Railway
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if domain:
        return f"https://{domain.rstrip('/')}"

    # Render
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url.rstrip("/")

    # Fly.io
    fly_app = os.getenv("FLY_APP_NAME")
    if fly_app:
        return f"https://{fly_app}.fly.dev"

    return f"http://localhost:{PORT}"


PUBLIC_URL = _detect_public_url()

# True once we're on a real host with a real address - the extension can reach us from anywhere
IS_PUBLIC = not PUBLIC_URL.startswith(("http://localhost", "http://127.0.0.1"))
