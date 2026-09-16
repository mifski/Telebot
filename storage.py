"""
User settings shared by the bot and the API server (they run in the same process)

Each user has: emoji, message_format, and optionally channel_id, channel_title,
link_code (the secret the Chrome extension uses) and paused.
"""

import json
import os
import secrets
import threading
from config import DATA_DIR

CONFIG_FILE = os.path.join(DATA_DIR, "user_configs.json")
DEFAULT_CONFIG = {"message_format": "now playing", "emoji": "🎵"}

# The bot and the API server run in different threads
_lock = threading.RLock()

def _load():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_users = _load()

def _save():
    """Write to a temp file first so a crash mid-write can't corrupt the settings"""
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp_file = CONFIG_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(_users, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, CONFIG_FILE)

def get_user(user_id):
    """A copy of the user's settings with defaults filled in"""
    with _lock:
        return {**DEFAULT_CONFIG, **_users.get(str(user_id), {})}

def update_user(user_id, **changes):
    """Change some settings and save. A value of None removes that setting."""
    with _lock:
        user = _users.setdefault(str(user_id), dict(DEFAULT_CONFIG))
        for key, value in changes.items():
            if value is None:
                user.pop(key, None)
            else:
                user[key] = value
        _save()
        return {**DEFAULT_CONFIG, **user}

def reset_user(user_id):
    """Back to the default format and emoji (keeps channel and connection code)"""
    return update_user(user_id, **DEFAULT_CONFIG)

def get_link_code(user_id, new=False):
    """The user's connection code for the Chrome extension, created if needed"""
    with _lock:
        code = get_user(user_id).get("link_code")
        if new or not code:
            code = secrets.token_urlsafe(12)
            update_user(user_id, link_code=code)
        return code

def find_user_by_code(code):
    """Returns (user_id, settings) for a connection code, or (None, None)"""
    if not code:
        return None, None
    with _lock:
        for user_id, user in _users.items():
            stored = user.get("link_code")
            if stored and secrets.compare_digest(stored.encode(), code.encode()):
                return user_id, {**DEFAULT_CONFIG, **user}
    return None, None

def users_with_channel(channel_id):
    """IDs of users whose posts go to this channel"""
    with _lock:
        return [user_id for user_id, user in _users.items() if str(user.get("channel_id")) == str(channel_id)]
