from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.services.task_service import TaskService
from app.services.notification_service import NotificationService

class CommandHandlers:
    def __init__(self, task_service: TaskService, notification_service: NotificationService):
        self.task_service = task_service
        self.notification_service = notification_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        self.notification_service.add_active_user(user_id)
        
        help_text = """
        📝 Shared Task Manager Bot 📝
        Commands: /add, /list, /edit, /delete, /help
        """
        await update.message.reply_text(help_text)

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            await update.message.reply_text("No tasks yet!")
            return
        
        message = "📋 Shared Task List:\n\n"
        for task in tasks:
            message += f"{task.id}. {task.description} ({task.priority})\n"
        
        await update.message.reply_text(message)
