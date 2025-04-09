from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from app.models.task import Task
from app.services.task_service import TaskService
from app.services.notification_service import NotificationService

class MessageHandlers:
    def __init__(self, task_service: TaskService, notification_service: NotificationService):
        self.task_service = task_service
        self.notification_service = notification_service

    async def handle_task_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'awaiting_task' in context.user_data:
            context.user_data['task_description'] = update.message.text
            context.user_data['awaiting_task'] = False
            context.user_data['awaiting_priority'] = True
            
            keyboard = [
                [InlineKeyboardButton("High 🔴", callback_data='priority_High')],
                [InlineKeyboardButton("Medium 🟡", callback_data='priority_Medium')],
                [InlineKeyboardButton("Low 🟢", callback_data='priority_Low')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Please select the task priority:",
                reply_markup=reply_markup
            )

    def register_handlers(self, application):
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_task_description)
        )
