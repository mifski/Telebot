"""
YouTube to Telegram Bot
Install: pip install -r requirements.txt
Run: python telebot.py   (also starts the API server the Chrome extension talks to)

Users connect a channel by adding the bot as admin, link the Chrome extension
with /connect, and customize their posts with Telegram commands.
"""

import sys

# Windows consoles often use a non-UTF-8 codepage (e.g. GBK) and crash on emoji
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from telegram import Update, BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Conflict, TelegramError
from telegram.warnings import PTBUserWarning
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from html import escape as h
import logging
import json
import os
import threading
import warnings
import storage
from api_server import build_message, run as run_api_server
from build_extension import build_zip
from config import BOT_TOKEN, DATA_DIR, IS_PUBLIC, PUBLIC_URL

# Harmless: the emoji picker's buttons belong to the conversation's own message
warnings.filterwarnings("ignore", message="If 'per_message=False'", category=PTBUserWarning)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# httpx logs every Telegram poll request - too noisy
logging.getLogger("httpx").setLevel(logging.WARNING)

if not BOT_TOKEN:
    sys.exit("ERROR: TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and put your token from @BotFather in it.")

# Conversation states
WAITING_FOR_FORMAT, WAITING_FOR_EMOJI = range(2)

CHANNELS_NOTIFIED_FILE = os.path.join(DATA_DIR, "channels_notified.json")

MAX_FORMAT_LENGTH = 100
MAX_EMOJI_LENGTH = 10

# Shown in Telegram's "/" menu
BOT_COMMANDS = [
    ("connect", "♡ get your secret code for the extension"),
    ("setformat", "✎ change the words before the title"),
    ("setemoji", "✿ change your little emoji"),
    ("preview", "👀 peek at how posts will look"),
    ("pause", "⏸ shh, stop posting for now"),
    ("resume", "▶ start posting again"),
    ("myconfig", "⚙ your current settings"),
    ("setchannel", "📢 connect a channel by hand"),
    ("downloadextension", "📦 get the Chrome extension"),
    ("installextension", "🔧 how to install it"),
    ("help", "📚 everything I can do"),
    ("support", "💌 get help"),
]

# Only answer commands in private chats - /connect shows a secret code
private = filters.ChatType.PRIVATE

def load_notified_channels():
    """Load list of channels already notified"""
    if os.path.exists(CHANNELS_NOTIFIED_FILE):
        with open(CHANNELS_NOTIFIED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def mark_channel_notified(chat_id):
    """Mark channel as notified"""
    channels = load_notified_channels()
    if str(chat_id) not in channels:
        channels.append(str(chat_id))
        with open(CHANNELS_NOTIFIED_FILE, 'w', encoding='utf-8') as f:
            json.dump(channels, f, indent=2, ensure_ascii=False)

def channel_line(user):
    """One line describing where the user's posts go"""
    if user.get("channel_id"):
        return f"📢 posting to: <b>{h(user.get('channel_title') or str(user['channel_id']))}</b> ♡"
    return "🌸 no channel yet — add me to your channel as an admin with \"Post Messages\" and I'll find it myself!"

async def reply(update: Update, text, **kwargs):
    await update.effective_message.reply_text(text, parse_mode='HTML', disable_web_page_preview=True, **kwargs)

async def dm(context: ContextTypes.DEFAULT_TYPE, user_id, text):
    """Message a user privately. Fails if they never pressed Start with the bot."""
    try:
        await context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
    except TelegramError as e:
        logging.info(f"Couldn't message user {user_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued"""
    user = storage.get_user(update.effective_user.id)

    await reply(update, f"""₊˚⊹ ♡ <b>hi hi! welcome!</b> ♡ ⊹˚₊

I'm your little music diary — whatever you play on YouTube, I'll tuck it into your Telegram channel for you (｡•ᴗ•｡)

<b>let's set you up (2 min!)</b>
୨୧ get the extension → /downloadextension
୨୧ add me to your channel as an admin with "Post Messages" — I'll notice and connect it myself ✨
୨୧ send /connect and paste your code into the extension
୨୧ press "send a test post" and watch the magic ♬

{channel_line(user)}

<b>make it yours ✎</b> /setformat · /setemoji · /preview
<b>you're in charge ⚙</b> /pause · /resume · /myconfig
everything I can do: /help""")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    await reply(update, """📚 ✿ <b>everything I can do</b> ✿

<b>୨୧ getting started</b>
/connect — your secret code for the extension
/setchannel — connect a channel by hand
/downloadextension — get the extension
/installextension — how to install it
/getchannelid — find a channel's ID

<b>୨୧ make it yours</b>
/setformat — the words before the title (like "now playing")
/setemoji — your little emoji
/preview — peek at how posts look
/reset — back to the cosy defaults

<b>୨୧ you're in charge</b>
/pause — shh, stop posting
/resume — start again ♡
/myconfig — your current settings
/newcode — fresh code (if someone got a peek at the old one)

need a hand? /support 💌""")

async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give the user their connection code for the extension"""
    user_id = update.effective_user.id
    code = storage.get_link_code(user_id)

    await reply(update, f"""🔗 ♡ <b>here's your secret code</b> ♡

<code>{code}</code>

tap it to copy, paste it into the extension, then press <b>save &amp; connect</b> ✨

{channel_line(storage.get_user(user_id))}

🔒 keep it just for you — anyone holding it can post to your channel. if it ever wanders off, /newcode gives you a fresh one!""")

async def new_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Replace the connection code so the old one stops working"""
    code = storage.get_link_code(update.effective_user.id, new=True)
    await reply(update, f"""🔄 ✿ <b>a brand new code, just for you</b> ✿

<code>{code}</code>

the old one is retired now ♡ pop this into the extension and press <b>save &amp; connect</b>.""")

async def set_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Connect a channel by ID or @username after checking both of us are admins there"""
    if not context.args:
        await reply(update, """📢 ✿ <b>connect a channel by hand</b> ✿

you probably don't need this! just add me to your channel as an admin and I'll notice all by myself ♡

but if you'd like to:
<code>/setchannel @yourchannel</code>
or
<code>/setchannel -1001234567890</code>

(/getchannelid shows where to find the ID)""")
        return

    target = context.args[0]
    user_id = update.effective_user.id
    try:
        chat = await context.bot.get_chat(target)
        bot_member = await chat.get_member(context.bot.id)
        user_member = await chat.get_member(user_id)
    except TelegramError:
        await reply(update, f"🥺 I can't find <b>{h(target)}</b> anywhere. add me to the channel as an admin first, then try again!")
        return

    if chat.type != "channel":
        await reply(update, "🌸 hmm, that's not a channel! make a Telegram channel and add me there as an admin ♡")
        return
    if bot_member.status != ChatMember.ADMINISTRATOR:
        await reply(update, f"🥺 I'm not an admin in <b>{h(chat.title)}</b> yet. could you add me with \"Post Messages\"? then I can share things for you!")
        return
    if user_member.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
        await reply(update, f"🔒 only an admin of <b>{h(chat.title)}</b> can connect it — just keeping everyone's channels safe ♡")
        return

    user = storage.update_user(user_id, channel_id=chat.id, channel_title=chat.title)
    await reply(update, f"✨ <b>connected!</b> ✨\n\n{channel_line(user)}\n\nnext up: /connect to link the extension ♡")

async def set_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to set message format"""
    await reply(update, """✎ ✿ <b>what should I say?</b> ✿

send me the little words you'd like before each video title ♡

<b>some ideas:</b>
୨୧ now playing
୨୧ currently obsessed with
୨୧ studying with
୨୧ vibing to
୨୧ today's comfort song

(or /cancel if you changed your mind!)""")
    return WAITING_FOR_FORMAT

async def receive_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save the message format"""
    new_format = update.message.text.strip()

    if len(new_format) > MAX_FORMAT_LENGTH:
        await reply(update, f"🌸 oop, that's a bit long! could you keep it under {MAX_FORMAT_LENGTH} characters? try again, or /cancel.")
        return WAITING_FOR_FORMAT

    storage.update_user(update.effective_user.id, message_format=new_format)
    await reply(update, f"✨ <b>all set!</b> ✨\n\nyour new words: <b>{h(new_format)}</b>\n\ntake a peek with /preview ♡")
    return ConversationHandler.END

async def set_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to set emoji"""
    emojis = ["🎵", "🎧", "🎼", "📻", "🎸", "🎹", "🎤", "🎺", "🎷", "📚", "☕", "✨"]
    keyboard = [
        [InlineKeyboardButton(e, callback_data=f"emoji:{e}") for e in emojis[i:i + 3]]
        for i in range(0, len(emojis), 3)
    ]

    await reply(
        update,
        "✿ <b>pick your little emoji</b> ✿\n\ntap one below, or send me any emoji you love ♡",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_FOR_EMOJI

async def emoji_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle emoji button press"""
    query = update.callback_query
    await query.answer()

    emoji = query.data.split(":", 1)[1]
    storage.update_user(query.from_user.id, emoji=emoji)

    await query.edit_message_text(
        f"✨ <b>lovely choice!</b> ✨\n\nyour emoji: {h(emoji)}\n\ntake a peek with /preview ♡",
        parse_mode='HTML'
    )
    return ConversationHandler.END

async def receive_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive custom emoji from user"""
    new_emoji = update.message.text.strip()

    if len(new_emoji) > MAX_EMOJI_LENGTH:
        await reply(update, "🌸 just an emoji or two, please! try again, or /cancel.")
        return WAITING_FOR_EMOJI

    storage.update_user(update.effective_user.id, emoji=new_emoji)
    await reply(update, f"✨ <b>lovely choice!</b> ✨\n\nyour emoji: {h(new_emoji)}\n\ntake a peek with /preview ♡")
    return ConversationHandler.END

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show preview of how messages will look"""
    # Built by the same function the API server uses, so the preview matches real posts
    sample = build_message(
        storage.get_user(update.effective_user.id),
        "Lofi Hip Hop Radio - Beats to Study/Relax to",
        "https://youtube.com/watch?v=jfKfPfyJRdk"
    )

    await reply(update, f"""👀 ✿ <b>a little peek</b> ✿

here's how your posts will look:

˚｡⋆｡˚ ⋆｡˚ ⋆｡˚ ⋆｡˚ ⋆｡˚
{sample}
˚｡⋆｡˚ ⋆｡˚ ⋆｡˚ ⋆｡˚ ⋆｡˚

cute, right? change it up with /setformat or /setemoji ♡""")

async def my_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current configuration"""
    user = storage.get_user(update.effective_user.id)
    posting = "⏸ on pause — /resume to wake me" if user.get("paused") else "♬ listening along — /pause for quiet"

    await reply(update, f"""⚙ ✿ <b>your little setup</b> ✿

{channel_line(user)}
<b>status:</b> {posting}
<b>emoji:</b> {h(user['emoji'])}
<b>your words:</b> {h(user['message_format'])}

<b>want to change something?</b>
୨୧ /setformat — new words
୨୧ /setemoji — new emoji
୨୧ /preview — see how it looks
୨୧ /reset — back to the cosy defaults
୨୧ /connect — link the extension""")

async def reset_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user configuration to defaults"""
    storage.reset_user(update.effective_user.id)
    await reply(update, """🫧 ✿ <b>freshly tidied!</b> ✿

back to the cosy defaults:
୨୧ emoji: 🎵
୨୧ words: now playing

your channel and secret code are exactly where you left them ♡ peek with /preview!""")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop posting without touching the extension"""
    storage.update_user(update.effective_user.id, paused=True)
    await reply(update, "⏸ <b>shh, I'll be quiet now</b> (-, - )…zzZ\n\nnothing will be posted until you send /resume ♡")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start posting again"""
    user = storage.update_user(update.effective_user.id, paused=None)
    await reply(update, f"♬ <b>I'm awake!</b> back to listening with you ٩(ᴗ͈ˬᴗ͈)۶\n\n{channel_line(user)}")

async def get_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help user get their channel ID"""
    await reply(update, """🆔 ✿ <b>finding your channel ID</b> ✿

you probably don't need it! add me to your channel as an admin with "Post Messages" and I'll connect it for you automatically ♡

but if you're curious:
୨୧ <b>way one:</b> after adding me, post anything in the channel — I'll whisper the ID back (just once)
୨୧ <b>way two:</b> forward any channel message to @userinfobot

channel IDs start with -100, and go with /setchannel ✨""")

async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Connect a channel when someone makes the bot its admin; disconnect when it's removed"""
    change = update.my_chat_member
    chat = change.chat
    if chat.type != "channel":
        return

    if change.new_chat_member.status == ChatMember.ADMINISTRATOR:
        # Only a channel admin can add the bot as admin, so from_user may connect it
        user = storage.update_user(change.from_user.id, channel_id=chat.id, channel_title=chat.title)
        text = f"✨ <b>yay, channel connected!</b> ✨\n\n{channel_line(user)}"
        if not getattr(change.new_chat_member, "can_post_messages", True):
            text += "\n\n🌸 one tiny thing — I don't have \"Post Messages\" yet! please switch it on in the channel's admin settings."
        if not user.get("link_code"):
            text += "\n\nnext up: send /connect to link the extension ♡"
        await dm(context, change.from_user.id, text)
        logging.info(f"Channel {chat.id} connected for user {change.from_user.id}")
    else:
        # Removed, or no longer an admin - can't post there anymore
        for user_id in storage.users_with_channel(chat.id):
            storage.update_user(user_id, channel_id=None, channel_title=None)
            await dm(context, user_id, f"🥺 I'm not an admin in <b>{h(chat.title)}</b> anymore, so I can't post there. add me back whenever you're ready — I'll be waiting ♡")
        logging.info(f"Channel {chat.id} disconnected")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """If nobody has connected this channel, explain how - once per channel"""
    if not update.channel_post:
        return
    chat = update.channel_post.chat
    if storage.users_with_channel(chat.id) or str(chat.id) in load_notified_channels():
        return

    await context.bot.send_message(
        chat_id=chat.id,
        text=f"♡ <b>hi! I'm here!</b> ♡\n\n"
             f"<b>this channel's ID:</b> <code>{chat.id}</code>\n\n"
             f"to send your YouTube videos here, message @{context.bot.username} privately with:\n"
             f"<code>/setchannel {chat.id}</code>\n\n"
             f"see you soon ✨",
        parse_mode='HTML'
    )
    mark_channel_notified(chat.id)
    logging.info(f"Sent setup hint to channel {chat.id}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await reply(update, "okay, never mind! ( ˘ ³˘)♡ /help if you need me.")
    return ConversationHandler.END

async def install_extension(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide instructions for installing the Chrome extension"""
    await reply(update, """🔧 ✿ <b>installing the extension</b> ✿

<b>୨୧ one</b> — /downloadextension, then unzip it into a folder you'll keep
<b>୨୧ two</b> — paste <code>chrome://extensions/</code> into Chrome's address bar
<b>୨୧ three</b> — flip on "Developer mode" (top right corner)
<b>୨୧ four</b> — click "Load unpacked" and choose that folder
<b>୨୧ five</b> — click the puzzle piece 🧩 in your toolbar and pin me so I'm easy to find
<b>୨୧ six</b> — send /connect, paste the code in, press <b>save &amp; connect</b>
<b>୨୧ seven</b> — press <b>send a test post</b>, then <b>start listening</b> and play something ♬

that's it — no need to keep anything running on your computer ✨

<b>if something's shy:</b>
୨୧ updated the extension? hit its refresh icon in chrome://extensions and reload your YouTube tabs
୨୧ test post unhappy? the popup tells you exactly why, in plain words
୨୧ still stuck? /support and I'll help 💌""")

async def download_extension(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the Chrome extension, built with this server's address inside it"""
    user_id = update.effective_user.id

    try:
        # Built fresh each time, so the extension always points at wherever this bot lives
        zip_bytes = build_zip(PUBLIC_URL)
    except OSError as e:
        await reply(update, "🥺 oh no, I can't put the extension together right now. please poke /support and it'll get fixed!")
        logging.error(f"Could not build the extension zip: {e}")
        return

    caption = (
        "📦 ♡ <b>here you go!</b> ♡\n\n"
        "it already knows where to find me, so there's nothing to type in ✨\n\n"
        "/installextension for the step-by-steps!"
    )
    if not IS_PUBLIC:
        caption += "\n\n🌸 heads up: this copy points at <code>localhost</code>, so it only works while the bot runs on your own computer."

    try:
        await update.message.reply_document(
            document=zip_bytes,
            filename="chrome_extension.zip",
            caption=caption,
            parse_mode='HTML'
        )
        logging.info(f"User {user_id} downloaded the extension (pointed at {PUBLIC_URL})")
    except TelegramError as e:
        await reply(update, "🥺 that didn't send properly — could you try again? or poke /support 💌")
        logging.error(f"Error sending extension to user {user_id}: {e}")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send support information"""
    await reply(update, """💌 ✿ <b>need a hand?</b> ✿

<b>the usual little hiccups:</b>
୨୧ nothing showing up? press <b>send a test post</b> in the extension — it says exactly what's wrong
୨୧ "no channel yet"? add me to your channel as an admin with "Post Messages"
୨୧ "no code yet"? send /connect and paste it in again
୨୧ posts went quiet? peek at /myconfig — you might be on /pause
୨୧ videos post after 10 seconds of playtime, so the ones you skip past stay private ♡
୨୧ press <b>start listening</b> in the popup, and refresh YouTube tabs opened before that

<b>still stuck? come say hi:</b>
୨୧ telegram: @physki
୨୧ email: izzychee1011@gmail.com

I'll get back to you soon ✨""")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors instead of crashing silently"""
    if isinstance(context.error, Conflict):
        logging.error("❌ Another copy of this bot is running with the same token (another terminal, or a deployed server). Stop it - only one can run at a time.")
        return
    logging.error("Error while handling an update", exc_info=context.error)

async def post_init(application: Application):
    """Fill Telegram's "/" command menu"""
    await application.bot.set_my_commands([BotCommand(name, description) for name, description in BOT_COMMANDS])

def start_api_server():
    """Run the extension API in the background so one command starts everything"""
    try:
        run_api_server()
    except OSError as e:
        logging.error(f"API server could not start ({e}). Is api_server.py already running on that port?")

def main():
    """Start the bot"""
    threading.Thread(target=start_api_server, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Command handlers
    commands = {
        "start": start,
        "help": help_command,
        "connect": connect,
        "newcode": new_code,
        "setchannel": set_channel,
        "preview": preview,
        "myconfig": my_config,
        "reset": reset_config,
        "pause": pause,
        "resume": resume,
        "getchannelid": get_channel_id,
        "installextension": install_extension,
        "downloadextension": download_extension,
        "support": support,
    }
    for name, callback in commands.items():
        application.add_handler(CommandHandler(name, callback, filters=private))

    # Conversation handler for setting format
    format_conv = ConversationHandler(
        entry_points=[CommandHandler("setformat", set_format, filters=private)],
        states={
            WAITING_FOR_FORMAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_format)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    application.add_handler(format_conv)

    # Conversation handler for setting emoji
    emoji_conv = ConversationHandler(
        entry_points=[CommandHandler("setemoji", set_emoji, filters=private)],
        states={
            WAITING_FOR_EMOJI: [
                CallbackQueryHandler(emoji_button, pattern="^emoji:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_emoji)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    application.add_handler(emoji_conv)

    # Emoji buttons still work if the conversation was lost (e.g. the bot restarted)
    application.add_handler(CallbackQueryHandler(emoji_button, pattern="^emoji:"))

    # Bot added to / removed from a channel
    application.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # Channel post handler
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))

    application.add_error_handler(error_handler)

    print("♡ bot is awake and listening! press Ctrl+C to stop ♡")
    print(f"♡ the extension will talk to: {PUBLIC_URL}")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
