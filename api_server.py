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
        data = request.json
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not channel_id or not message:
            return jsonify({
                "success": False,
                "error": "Missing channel_id or message"
            }), 400
        
        if not BOT_TOKEN:
            return jsonify({
                "success": False,
                "error": "Bot token not configured on server"
            }), 500
        
        # Send message to Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        response = requests.post(url, json={
            "chat_id": channel_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        })
        
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                "success": True,
                "message": "Video posted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('description', 'Unknown error')
            }), 400
            
    except Exception as e:
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