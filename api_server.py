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

app = Flask(__name__)
CORS(app)  # Allow requests from Chrome extension

CONFIG_FILE = "user_configs.json"

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