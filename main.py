from flask import Flask, jsonify
from telegram.ext import Application
from config import Config
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService
from app.services.notification_service import NotificationService
from app.handlers.command_handlers import CommandHandlers
import logging
from threading import Thread

# Initialize services
config = Config()
task_repo = TaskRepository(config.DATABASE_URL)
task_service = TaskService(task_repo)

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

def setup_bot():
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    notification_service = NotificationService(application.bot)
    handlers = CommandHandlers(task_service, notification_service)

    # Register handlers
    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(CommandHandler('list', handlers.list_tasks))
    # ... register other handlers

    return application

def run_flask():
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    bot_app = setup_bot()
    bot_app.run_polling()
