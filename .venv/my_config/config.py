import os
from dotenv import load_dotenv
from dataclasses import dataclass
from aiogram import Bot



@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

@dataclass
class Config:
    tg_bot: TgBot

def load_config(path: str | None = None) -> Config:
    load_dotenv()
    admin_ids = [int(id_.strip()) for id_ in os.getenv('ADMIN_IDS').split(',')]
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN'),
            admin_ids=admin_ids
        )
    )



