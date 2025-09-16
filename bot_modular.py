import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
N8N_WEBHOOK_URL = "https://n8n.lotwizard.us/webhook/telegram-bot-modular"

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

def send_to_n8n(data):
    """Send data to n8n webhook"""
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully sent data to n8n: {response.status_code}")
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to n8n: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    data = {
        "type": "command",
        "command": "start",
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "timestamp": update.message.date.isoformat()
    }
    
    n8n_response = send_to_n8n(data)
    
    welcome_message = "Hello! I'm your n8n bridge bot (MODULAR VERSION). Send me any message and I'll forward it to your n8n workflow."
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user = update.effective_user
    message = update.message
    
    data = {
        "type": "message",
        "message_id": message.message_id,
        "text": message.text,
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "chat_id": message.chat_id,
        "timestamp": message.date.isoformat()
    }
    
    n8n_response = send_to_n8n(data)
    
    if n8n_response and isinstance(n8n_response, dict) and 'reply' in n8n_response:
        await update.message.reply_text(n8n_response['reply'])
    else:
        await context.bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction="👍"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    user = update.effective_user
    message = update.message
    photo = message.photo[-1]  # Get the highest resolution photo
    
    data = {
        "type": "photo",
        "message_id": message.message_id,
        "photo_file_id": photo.file_id,
        "caption": message.caption,
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "chat_id": message.chat_id,
        "timestamp": message.date.isoformat()
    }
    
    n8n_response = send_to_n8n(data)
    
    if n8n_response and isinstance(n8n_response, dict) and 'reply' in n8n_response:
        await update.message.reply_text(n8n_response['reply'])
    else:
        await context.bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction="👍"
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages"""
    user = update.effective_user
    message = update.message
    document = message.document
    
    data = {
        "type": "document",
        "message_id": message.message_id,
        "document_file_id": document.file_id,
        "document_name": document.file_name,
        "document_mime_type": document.mime_type,
        "caption": message.caption,
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "chat_id": message.chat_id,
        "timestamp": message.date.isoformat()
    }
    
    n8n_response = send_to_n8n(data)
    
    if n8n_response and isinstance(n8n_response, dict) and 'reply' in n8n_response:
        await update.message.reply_text(n8n_response['reply'])
    else:
        await context.bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction="👍"
        )

def main():
    """Start the bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    logger.info("Bot is starting... (MODULAR VERSION)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()