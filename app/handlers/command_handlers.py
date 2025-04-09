from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler
from app.models.task import Task
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
        📝 *Shared Task Manager Bot* 📝
        
        *Commands:*
        /start - Show this message
        /add - Add a new task (notifies everyone)
        /list - Show all tasks
        /edit - Edit a task
        /delete - Delete a task
        /help - Show help
        
        All changes are visible to everyone immediately!
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
        📝 *Available Commands* 📝
        
        */add* - Add a new shared task
        */list* - Show all tasks
        */edit* - Edit an existing task
        */delete* - Remove a task
        */help* - Show this help message
        
        Tasks can have High, Medium, or Low priority.
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            await update.message.reply_text("No tasks yet! Use /add to create one.")
            return
        
        message = "📋 *Shared Task List* 📋\n\n"
        for task in tasks:
            creator = f" (by {task.created_by})" if task.created_by else ""
            message += f"{task.id}. {task.priority_icon} *{task.description}*{creator}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')

    def register_handlers(self, application):
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CommandHandler('list', self.list_tasks))
