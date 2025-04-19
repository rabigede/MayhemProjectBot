from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from my_config.config import load_config
import asyncio
import aiosqlite
from database.requests import *
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
from handlers import user_handlers
from keyboards.menu import set_main_menu
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from handlers.user_handlers import check_time, ring_time


async def main() -> None:
    config = load_config()

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await set_main_menu(bot)
    dp.include_router(user_handlers.router)

    asyncio.create_task(check_time(ring_time, bot))
    await database_on()

    await dp.start_polling(bot)


asyncio.run(main())
