# Configuration file for deployment

# Bot Token - Set this as environment variable: TELEGRAM_BOT_TOKEN
# Don't hardcode it here!

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = int(__import__('os').getenv('PORT', 5000))
DEBUG_MODE = __import__('os').getenv('ENVIRONMENT', 'local') == 'local'

# Bot Configuration
CONFIG_FILE = "user_configs.json"
LOGGING_LEVEL = "INFO"

# Deployment Info
DEPLOYMENT_TYPE = __import__('os').getenv('ENVIRONMENT', 'local')  # 'local', 'production'
