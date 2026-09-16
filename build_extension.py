"""
Builds chrome_extension.zip from the extension/ folder.

The bot's address is stamped into background.js as it's zipped, so whoever
downloads the extension with /downloadextension never has to type a URL.

Rebuild the file on disk:  python build_extension.py
"""

import io
import os
import zipfile
from config import BASE_DIR, PUBLIC_URL

EXTENSION_DIR = os.path.join(BASE_DIR, "extension")
ZIP_PATH = os.path.join(BASE_DIR, "chrome_extension.zip")
PLACEHOLDER = "__SERVER_URL__"

# Everything the extension needs, in the order Chrome cares about least
FILES = ["manifest.json", "background.js", "content.js", "popup.html", "popup.js"]


def build_zip(server_url=None):
    """Return the extension as zip bytes, pointed at server_url"""
    server_url = (server_url or PUBLIC_URL).rstrip("/")
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            path = os.path.join(EXTENSION_DIR, name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Only background.js holds the placeholder, but replacing everywhere is harmless
            archive.writestr(name, content.replace(PLACEHOLDER, server_url))

    return buffer.getvalue()


if __name__ == "__main__":
    data = build_zip()
    with open(ZIP_PATH, "wb") as f:
        f.write(data)
    print(f"Built {ZIP_PATH} ({len(data):,} bytes), pointed at {PUBLIC_URL}")
