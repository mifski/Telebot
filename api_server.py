"""
API Server for Chrome Extension to fetch user configurations
Install: pip install flask flask-cors python-telegram-bot
Run: python api_server.py

This creates an API that the extension can call to get message format settings
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import requests
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow requests from Chrome extension

CONFIG_FILE = "user_configs.json"
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def load_configs():
    """Load user configurations from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/api/config/<user_id>', methods=['GET'])
def get_user_config(user_id):
    """Get configuration for a specific user"""
    configs = load_configs()
    
    if user_id in configs:
        return jsonify({
            "success": True,
            "config": configs[user_id]
        })
    else:
        # Return default config
        return jsonify({
            "success": True,
            "config": {
                "message_format": "now playing",
                "emoji": "🎵"
            }
        })

@app.route('/api/send-video', methods=['POST'])
def send_video():
    """Receive video from extension and post to Telegram"""
    try:
        logger.debug(f"Received request to /api/send-video")
        logger.debug(f"Request data: {request.json}")
        
        data = request.json
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        message = data.get('message')
        
        logger.info(f"Processing video for user {user_id} to channel {channel_id}")
        
        if not channel_id or not message:
            logger.error(f"Missing required fields - channel_id: {channel_id}, message: {bool(message)}")
            return jsonify({
                "success": False,
                "error": "Missing channel_id or message"
            }), 400
        
        if not BOT_TOKEN:
            logger.error("Bot token not configured!")
            return jsonify({
                "success": False,
                "error": "Bot token not configured on server"
            }), 500
        
        logger.debug(f"Bot token found: {BOT_TOKEN[:10]}...")
        
        # Send message to Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        logger.debug(f"Sending to Telegram: {url}")
        
        payload = {
            "chat_id": channel_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        logger.debug(f"Payload: {payload}")
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        logger.debug(f"Telegram response: {result}")
        
        if result.get('ok'):
            logger.info(f"✅ Message sent successfully to {channel_id}")
            return jsonify({
                "success": True,
                "message": "Video posted successfully"
            })
        else:
            error_desc = result.get('description', 'Unknown error')
            logger.error(f"❌ Telegram error: {error_desc}")
            return jsonify({
                "success": False,
                "error": error_desc
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Exception in send_video: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 API Server running on http://0.0.0.0:{port}")
    print(f"Extension can fetch configs from: http://localhost:{port}/api/config/{{user_id}}")
    
    # Use debug mode only for local development
    debug_mode = os.getenv('ENVIRONMENT', 'local') == 'local'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)