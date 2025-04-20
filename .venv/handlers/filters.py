from my_config.config import load_config
from aiogram import Bot, Dispatcher
from aiogram.filters import BaseFilter
from aiogram.types import Message

config = load_config()

class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int] = config.tg_bot.admin_ids) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids