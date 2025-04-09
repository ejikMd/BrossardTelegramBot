from typing import Set, Optional
from telegram import Bot
from app.models.task import Task
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_users: Set[str] = set()

    async def notify_task_created(self, task: Task, exclude_user_id: Optional[str] = None):
        message = (
            f"📢 New task created by {task.created_by}:\n\n"
            f"{task.priority_icon} *{task.description}*\n"
            f"Priority: {task.priority}"
        )
        await self._notify_all(message, exclude_user_id)

    async def notify_task_updated(self, task: Task, exclude_user_id: Optional[str] = None):
        message = (
            f"✏️ Task updated by {task.created_by}:\n\n"
            f"{task.priority_icon} *{task.description}*\n"
            f"Priority: {task.priority}"
        )
        await self._notify_all(message, exclude_user_id)

    async def notify_task_deleted(self, description: str, deleted_by: str, exclude_user_id: Optional[str] = None):
        message = (
            f"🗑 Task deleted by {deleted_by}:\n\n"
            f"*{description}*"
        )
        await self._notify_all(message, exclude_user_id)

    async def _notify_all(self, message: str, exclude_user_id: Optional[str] = None):
        for user_id in self.active_users:
            if user_id != exclude_user_id:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {user_id}: {e}")

    def add_active_user(self, user_id: str):
        self.active_users.add(user_id)
