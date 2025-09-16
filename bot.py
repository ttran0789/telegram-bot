import os
import logging
import requests
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Primary bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

# Secondary bot configuration (TVO)
TELEGRAM_BOT_TOKEN_TVO = os.getenv('TELEGRAM_BOT_TOKEN_TVO')
N8N_WEBHOOK_URL_TVO = os.getenv('N8N_WEBHOOK_URL_TVO')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
if not N8N_WEBHOOK_URL:
    raise ValueError("N8N_WEBHOOK_URL not found in environment variables")
if not TELEGRAM_BOT_TOKEN_TVO:
    raise ValueError("TELEGRAM_BOT_TOKEN_TVO not found in environment variables")
if not N8N_WEBHOOK_URL_TVO:
    raise ValueError("N8N_WEBHOOK_URL_TVO not found in environment variables")

def send_to_n8n(data, webhook_url):
    """Send data to n8n webhook"""
    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully sent data to n8n: {response.status_code}")
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to n8n: {e}")
        return None

def create_start_handler(webhook_url):
    """Create a start command handler with specific webhook URL"""
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

        n8n_response = send_to_n8n(data, webhook_url)

        welcome_message = "Hello! I'm your n8n bridge bot. Send me any message and I'll forward it to your n8n workflow."
        await update.message.reply_text(welcome_message)

    return start

def create_message_handler(webhook_url):
    """Create a message handler with specific webhook URL"""
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

        n8n_response = send_to_n8n(data, webhook_url)

        if n8n_response and isinstance(n8n_response, dict) and 'reply' in n8n_response:
            await update.message.reply_text(n8n_response['reply'])
        else:
            await context.bot.set_message_reaction(
                chat_id=message.chat_id,
                message_id=message.message_id,
                reaction="👍"
            )

    return handle_message

def create_photo_handler(webhook_url):
    """Create a photo handler with specific webhook URL"""
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

        n8n_response = send_to_n8n(data, webhook_url)

        if n8n_response and isinstance(n8n_response, dict) and 'reply' in n8n_response:
            await update.message.reply_text(n8n_response['reply'])
        else:
            await context.bot.set_message_reaction(
                chat_id=message.chat_id,
                message_id=message.message_id,
                reaction="👍"
            )

    return handle_photo

def create_document_handler(webhook_url):
    """Create a document handler with specific webhook URL"""
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

        n8n_response = send_to_n8n(data, webhook_url)

        if n8n_response and isinstance(n8n_response, dict) and 'reply' in n8n_response:
            await update.message.reply_text(n8n_response['reply'])
        else:
            await context.bot.set_message_reaction(
                chat_id=message.chat_id,
                message_id=message.message_id,
                reaction="👍"
            )

    return handle_document

async def run_bot(token, webhook_url, bot_name):
    """Run a single bot instance"""
    application = Application.builder().token(token).build()

    # Add handlers with specific webhook URL
    application.add_handler(CommandHandler("start", create_start_handler(webhook_url)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_message_handler(webhook_url)))
    application.add_handler(MessageHandler(filters.PHOTO, create_photo_handler(webhook_url)))
    application.add_handler(MessageHandler(filters.Document.ALL, create_document_handler(webhook_url)))

    logger.info(f"{bot_name} is starting...")

    # Initialize and start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    return application

async def main():
    """Start both bots concurrently"""
    try:
        # Create both bot instances
        primary_app = await run_bot(TELEGRAM_BOT_TOKEN, N8N_WEBHOOK_URL, "Primary Bot")
        tvo_app = await run_bot(TELEGRAM_BOT_TOKEN_TVO, N8N_WEBHOOK_URL_TVO, "TVO Bot")

        logger.info("Both bots are running. Press Ctrl+C to stop.")

        # Keep the bots running
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("Stopping both bots...")
        # Properly shutdown both applications
        await primary_app.updater.stop()
        await primary_app.stop()
        await primary_app.shutdown()

        await tvo_app.updater.stop()
        await tvo_app.stop()
        await tvo_app.shutdown()

        logger.info("Both bots stopped.")

if __name__ == '__main__':
    asyncio.run(main())