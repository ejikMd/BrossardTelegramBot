from telegram import Bot
from typing import Set
from app.models.task import Task

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_users: Set[str] = set()

    async def notify_all(self, message: str, exclude_user_id: str = None):
        for user_id in self.active_users:
            if user_id != exclude_user_id:
                try:
                    await self.bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    print(f"Failed to notify user {user_id}: {e}")

    def add_active_user(self, user_id: str):
        self.active_users.add(user_id)
