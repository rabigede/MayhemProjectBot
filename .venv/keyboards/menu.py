from aiogram import Bot
from aiogram.types import BotCommand
import asyncio

async def set_main_menu(bot: Bot):

    main_menu_commands = [
        BotCommand(command='/menu',
                   description='ВЕРНУТЬСЯ В ГЛАВНОЕ МЕНЮ'),
        BotCommand(command='/help',
                   description='📚 Руководство'),
        BotCommand(command='/start',
                   description='🔄 Перезапустить бота'),
        BotCommand(command='/support',
                   description='⚙ Поддержка'),
    ]
    await bot.set_my_commands(main_menu_commands)

