"""
Telegram Bot Server - With Configuration Management
Install: pip install python-telegram-bot
Run: python bot_server.py

Users can configure message format via Telegram commands!
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
import logging
import json
import os

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load bot token from environment variable for security
import os
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")

# Conversation states
WAITING_FOR_FORMAT, WAITING_FOR_EMOJI = range(2)

# File to store user configurations
CONFIG_FILE = "user_configs.json"

# Load/Save configurations
def load_configs():
    """Load user configurations from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_configs(configs):
    """Save user configurations to file"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)

# Global config storage
user_configs = load_configs()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued"""
    user_id = str(update.effective_user.id)
    
    # Initialize default config if new user
    if user_id not in user_configs:
        user_configs[user_id] = {
            "message_format": "now playing",
            "emoji": "🎵"
        }
        save_configs(user_configs)
    
    welcome_text = """
🎵 *Welcome to YouTube to Telegram Bot!*

I can automatically post YouTube videos you're watching to your Telegram channel.

*Quick Setup:*
1. Install the Chrome extension
2. Create a channel and add me as admin
3. Use /getchannelid to get your channel ID
4. Configure the extension with your channel ID

*Customize Your Messages:*
• /setformat - Change message format
• /setemoji - Change emoji
• /preview - See how your messages will look
• /myconfig - View your current settings

*Other Commands:*
• /help - Full instructions
• /getchannelid - Get your channel ID
• /support - Get help

Let's get started! 🚀
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
*📚 Complete Guide*

*Step 1: Setup*
1. Use /downloadextension to get the Chrome extension
2. Use /installextension for detailed installation steps
3. Create a Telegram channel
4. Add this bot as admin (with "Post Messages")
5. Use /getchannelid to get your channel ID
6. Enter channel ID in extension

*Step 2: Customize (Optional)*
• /setformat - Change your message format
• /setemoji - Change your emoji
• /preview - Preview your messages

*Step 3: Start Monitoring*
• Click "Start Monitoring" in extension
• Play YouTube videos
• Watch them appear in your channel!

*Configuration Commands:*
/setformat - Set message text (e.g., "now playing", "listening to")
/setemoji - Set emoji (e.g., 🎵, 🎧, 📻)
/preview - Preview how messages will look
/myconfig - View current settings
/reset - Reset to default settings

*Utility Commands:*
/downloadextension - Download Chrome extension ZIP
/installextension - Installation instructions
/getchannelid - Get your channel ID
/help - Show this message
/support - Contact support
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to set message format"""
    await update.message.reply_text(
        "📝 *Set Message Format*\n\n"
        "Send me the text you want before the video title.\n\n"
        "*Examples:*\n"
        "• now playing\n"
        "• currently listening to\n"
        "• studying with\n"
        "• vibing to\n\n"
        "Or send /cancel to cancel.",
        parse_mode='Markdown'
    )
    return WAITING_FOR_FORMAT

async def receive_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save the message format"""
    user_id = str(update.effective_user.id)
    new_format = update.message.text.strip()
    
    # Update config
    if user_id not in user_configs:
        user_configs[user_id] = {"emoji": "🎵"}
    
    user_configs[user_id]["message_format"] = new_format
    save_configs(user_configs)
    
    await update.message.reply_text(
        f"✅ *Format Updated!*\n\n"
        f"Your new format: `{new_format}`\n\n"
        f"Use /preview to see how it looks!",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def set_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to set emoji"""
    keyboard = [
        [
            InlineKeyboardButton("🎵", callback_data="emoji:🎵"),
            InlineKeyboardButton("🎧", callback_data="emoji:🎧"),
            InlineKeyboardButton("🎼", callback_data="emoji:🎼"),
        ],
        [
            InlineKeyboardButton("📻", callback_data="emoji:📻"),
            InlineKeyboardButton("🎸", callback_data="emoji:🎸"),
            InlineKeyboardButton("🎹", callback_data="emoji:🎹"),
        ],
        [
            InlineKeyboardButton("🎤", callback_data="emoji:🎤"),
            InlineKeyboardButton("🎺", callback_data="emoji:🎺"),
            InlineKeyboardButton("🎷", callback_data="emoji:🎷"),
        ],
        [
            InlineKeyboardButton("📚", callback_data="emoji:📚"),
            InlineKeyboardButton("☕", callback_data="emoji:☕"),
            InlineKeyboardButton("✨", callback_data="emoji:✨"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Choose Your Emoji*\n\n"
        "Pick one from below, or send me any emoji you like!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAITING_FOR_EMOJI

async def emoji_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle emoji button press"""
    query = update.callback_query
    await query.answer()
    
    emoji = query.data.split(":")[1]
    user_id = str(query.from_user.id)
    
    # Update config
    if user_id not in user_configs:
        user_configs[user_id] = {"message_format": "now playing"}
    
    user_configs[user_id]["emoji"] = emoji
    save_configs(user_configs)
    
    await query.edit_message_text(
        f"✅ *Emoji Updated!*\n\n"
        f"Your new emoji: {emoji}\n\n"
        f"Use /preview to see how it looks!",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def receive_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive custom emoji from user"""
    user_id = str(update.effective_user.id)
    new_emoji = update.message.text.strip()
    
    # Update config
    if user_id not in user_configs:
        user_configs[user_id] = {"message_format": "now playing"}
    
    user_configs[user_id]["emoji"] = new_emoji
    save_configs(user_configs)
    
    await update.message.reply_text(
        f"✅ *Emoji Updated!*\n\n"
        f"Your new emoji: {new_emoji}\n\n"
        f"Use /preview to see how it looks!",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show preview of how messages will look"""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_configs:
        user_configs[user_id] = {
            "message_format": "now playing",
            "emoji": "🎵"
        }
        save_configs(user_configs)
    
    config = user_configs[user_id]
    emoji = config.get("emoji", "🎵")
    message_format = config.get("message_format", "now playing")
    
    # Create preview
    preview_text = f"{emoji} {message_format}\n\n[Lofi Hip Hop Radio - Beats to Study/Relax to](https://youtube.com/watch?v=jfKfPfyJRdk)"
    
    await update.message.reply_text(
        "*📱 Message Preview*\n\n"
        "This is how your messages will appear:\n\n"
        "─────────────────\n" +
        preview_text + "\n"
        "─────────────────\n\n"
        "Like it? Use /setformat or /setemoji to change!",
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def my_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current configuration"""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_configs:
        user_configs[user_id] = {
            "message_format": "now playing",
            "emoji": "🎵"
        }
        save_configs(user_configs)
    
    config = user_configs[user_id]
    
    config_text = f"""
*⚙️ Your Current Settings*

*Emoji:* {config.get('emoji', '🎵')}
*Message Format:* `{config.get('message_format', 'now playing')}`

*Commands to Change:*
• /setformat - Change message text
• /setemoji - Change emoji
• /preview - See how it looks
• /reset - Reset to defaults
    """
    
    await update.message.reply_text(config_text, parse_mode='Markdown')

async def reset_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user configuration to defaults"""
    user_id = str(update.effective_user.id)
    
    user_configs[user_id] = {
        "message_format": "now playing",
        "emoji": "🎵"
    }
    save_configs(user_configs)
    
    await update.message.reply_text(
        "🔄 *Settings Reset!*\n\n"
        "Your configuration has been reset to:\n"
        "• Emoji: 🎵\n"
        "• Format: `now playing`\n\n"
        "Use /preview to see it!",
        parse_mode='Markdown'
    )

async def get_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help user get their channel ID"""
    instruction_text = """
*🆔 Get Your Channel ID*

*Method 1: Forward Message*
1. Forward ANY message from your channel to @userinfobot
2. It will reply with your channel ID
3. Copy the ID (e.g., -1001234567890)

*Method 2: Use This Bot*
1. Add me as admin to your channel
2. Post any message in the channel
3. I'll automatically detect it and tell you the ID

*Method 3: Web Telegram*
1. Go to web.telegram.org
2. Open your channel
3. Check the URL for the number after #

*Your channel ID starts with -100*
Use it in the Chrome extension settings!
    """
    
    await update.message.reply_text(instruction_text, parse_mode='Markdown')

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect when bot is added to a channel and show ID"""
    if update.channel_post:
        chat_id = update.channel_post.chat.id
        chat_title = update.channel_post.chat.title
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ *Bot Added Successfully!*\n\n"
                 f"*Channel:* {chat_title}\n"
                 f"*Channel ID:* `{chat_id}`\n\n"
                 f"Copy this ID and paste it in your Chrome extension settings!",
            parse_mode='Markdown'
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ Cancelled. Use /help to see available commands.",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def install_extension(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide instructions for installing the Chrome extension"""
    install_text = """
*🔧 Install Chrome Extension*

*Step 1: Download Extension*
1. Use /downloadextension to get the ZIP file
2. Extract it to a folder on your computer

*Step 2: Open Chrome Extensions Page*
1. Open Chrome browser
2. Copy this in the address bar: `chrome://extensions/`
3. Press Enter

*Step 3: Enable Developer Mode*
1. Look for "Developer mode" toggle (top right)
2. Click to turn it ON

*Step 4: Load Extension*
1. Click "Load unpacked" button
2. Navigate to where you extracted the ZIP file
3. Select the folder and click "Select Folder"

*Step 5: Verify Installation*
1. Look for the extension icon in Chrome toolbar
2. It should appear as a puzzle piece icon
3. Pin it to your toolbar for easy access

*Step 6: Configure Extension*
1. Click the extension icon
2. Enter your Telegram Channel ID
3. Save settings

*Quick Download:*
Use /downloadextension to get your ZIP file right now!

*Note:*
If you don't know your Channel ID, use /getchannelid first!

*Troubleshooting:*
• Extension not showing? Go to chrome://extensions and ensure it's enabled
• Want to reload? Click the refresh icon on the extension card
• Still issues? Use /support for help
    """
    await update.message.reply_text(install_text, parse_mode='Markdown')

async def download_extension(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the Chrome extension ZIP file to user"""
    user_id = update.effective_user.id
    
    try:
        # Try to find the extension ZIP file
        extension_files = [
            "chrome_extension.zip",
            "chrome_extension.zip.zip",
            "extension.zip"
        ]
        
        extension_zip_path = None
        for filename in extension_files:
            if os.path.exists(filename):
                extension_zip_path = filename
                break
        
        # Check if file exists
        if extension_zip_path is None:
            await update.message.reply_text(
                "❌ *Error:*\n\n"
                "Extension file not found. Please contact support.",
                parse_mode='Markdown'
            )
            logging.warning(f"Extension ZIP file not found")
            return
        
        # Send the file
        await update.message.reply_document(
            document=open(extension_zip_path, 'rb'),
            caption="📦 *Your Chrome Extension*\n\n"
                   "Use /installextension for detailed installation instructions!",
            parse_mode='Markdown'
        )
        
        logging.info(f"User {user_id} downloaded the extension from {extension_zip_path}")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error sending file:*\n\n{str(e)}\n\n"
            "Please try again or contact /support",
            parse_mode='Markdown'
        )
        logging.error(f"Error sending extension to user {user_id}: {str(e)}")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send support information"""
    support_text = """
*💬 Need Help?*

*Common Issues:*
1. Bot not posting? Check it's admin with "Post Messages"
2. Extension not working? Reload it from chrome://extensions
3. Wrong channel ID? Use /getchannelid
4. Need to install extension? Use /installextension

*Contact:*
• Telegram: @physki
• Email: izzychee1011@gmail.com

*Resources:*
• Installation guide: /installextension
• All commands: /help
• Get channel ID: /getchannelid
    """
    await update.message.reply_text(support_text, parse_mode='Markdown')

def main():
    """Start the bot"""
    try:
        if not BOT_TOKEN:
            print("ERROR: Bot token not found! Make sure to set your bot token!")
            print("You can set it by running: set TELEGRAM_BOT_TOKEN=your_token_here")
            return
            
        print(f"Starting bot with token: {BOT_TOKEN[:5]}...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("preview", preview))
        application.add_handler(CommandHandler("myconfig", my_config))
        application.add_handler(CommandHandler("reset", reset_config))
        application.add_handler(CommandHandler("getchannelid", get_channel_id))
        application.add_handler(CommandHandler("installextension", install_extension))
        application.add_handler(CommandHandler("downloadextension", download_extension))
        application.add_handler(CommandHandler("support", support))
    except Exception as e:
        print(f"ERROR: Failed to start the bot: {str(e)}")
        print("Please check your bot token and internet connection.")
        return
    
    # Conversation handler for setting format
    format_conv = ConversationHandler(
        entry_points=[CommandHandler("setformat", set_format)],
        states={
            WAITING_FOR_FORMAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_format)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(format_conv)
    
    # Conversation handler for setting emoji
    emoji_conv = ConversationHandler(
        entry_points=[CommandHandler("setemoji", set_emoji)],
        states={
            WAITING_FOR_EMOJI: [
                CallbackQueryHandler(emoji_button, pattern="^emoji:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_emoji)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(emoji_conv)
    
    # Channel post handler
    application.add_handler(
        MessageHandler(filters.ChatType.CHANNEL, handle_channel_post)
    )
    
    print("🎵 Bot is running with configuration management!")
    print("Users can now customize their message format via Telegram commands")
    print("Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()