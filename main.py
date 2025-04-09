from flask import Flask, jsonify
from telegram.ext import Application
from config import Config
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService
from app.services.notification_service import NotificationService
from app.handlers.command_handlers import CommandHandlers
from app.handlers.message_handlers import MessageHandlers
import logging
from threading import Thread

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

def setup_bot():
    config = Config()
    
    # Initialize services
    task_repo = TaskRepository(config.DATABASE_URL)
    task_service = TaskService(task_repo)
    
    # Create bot application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    notification_service = NotificationService(application.bot)
    
    # Register handlers
    command_handlers = CommandHandlers(task_service, notification_service)
    command_handlers.register_handlers(application)
    
    message_handlers = MessageHandlers(task_service, notification_service)
    message_handlers.register_handlers(application)
    
    return application

def run_flask():
    config = Config()
    app.run(host='0.0.0.0', port=config.PORT)

if __name__ == '__main__':
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Start Telegram bot
    try:
        bot_app = setup_bot()
        bot_app.run_polling()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
