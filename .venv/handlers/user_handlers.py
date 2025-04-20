import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from handlers.filters import IsAdmin
from lexicon.lexicon import *
from keyboards.inline import *
from aiogram.enums import ParseMode
from random import randint, random
import sqlite3
from datetime import date, timedelta, datetime, time
from keyboards.paginate_book import *
from database.requests import *
from pyexpat.errors import messages

router = Router()
ring_time = (0, 0, 10)


def random_quote(a=general_quotes):
    len_ = len(a)
    index_ = randint(0, len_ - 1)
    return a[index_]


def check_name(name):
    if type(name) == type(None):
        return ''
    else:
        return name


def get_time_until_next_ring(ring_time: tuple) -> str:
    now = datetime.now()
    today_ring = now.replace(hour=ring_time[0], minute=ring_time[1], second=ring_time[2], microsecond=0)

    if now >= today_ring:
        next_ring = today_ring + timedelta(days=1)
    else:
        next_ring = today_ring

    time_left = next_ring - now

    total_seconds = int(time_left.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours} час{'а' if 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20) else 'ов'}")
    if minutes > 0:
        parts.append(
            f"{minutes} минут{'у' if minutes == 1 else 'ы' if 2 <= minutes % 10 <= 4 and minutes % 100 != 12 else ''}")
    if not parts:
        return "меньше минуты"

    return " ".join(parts)


@router.message(CommandStart())
async def process_start_command(message: Message):
    is_existed = await user_exists(message.from_user.id)
    if not is_existed:
        await check_db_structure()

        await add_user(user_id=message.from_user.id,
                       chat_id=message.chat.id,
                       user_name=(check_name(message.from_user.first_name) + check_name(message.from_user.last_name))
                       )
    await message.answer(
        text=COMMANDS_RU['/start'],
        reply_markup=start_kb
    )


@router.message(Command(commands='help'))
async def show_help(message: Message):
    content, keyboard = build_page(0)
    await message.answer(text=content, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "no_action")
async def handle_no_action(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("page_"))
async def handle_page_change(callback: CallbackQuery):
    page_num = int(callback.data.split("_")[1])
    content, keyboard = build_page(page_num)
    await callback.message.edit_text(text=content, reply_markup=keyboard.as_markup())
    await callback.answer()


@router.message(Command(commands='support'))
async def process_help_command(message: Message):
    await message.answer(text=COMMANDS_RU['/support'])


@router.message(Command(commands='add_task'), IsAdmin())
async def process_help_command(message: Message):
    await message.answer(text='отправь видео и текст к нему(в одном сообщении)')


@router.message(Command(commands='menu'))
async def process_help_command(message: Message):
    await message.answer(
        text=LEXICON_RU['nice to meet you']
    )
    await message.answer_animation(
        animation='https://tenor.com/ru/view/buildings-collapse-collapse-'
                  'fight-club-explosion-fight-club-tyler-durden-gif-17408378'
    )
    await message.answer(
        text=random_quote(),
        reply_markup=general_kb
    )


@router.callback_query(F.data == 'start game')
async def start_game_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['nice to meet you']
    )

    await callback.answer(
        text=LEXICON_RU['disclaimer'],
        show_alert=True
    )

    await callback.message.answer_animation(
        animation=LEXICON_RU['buildings_explode_gif']
    )

    await asyncio.sleep(1)
    await callback.message.answer(
        text=LEXICON_RU['first_meet'],
        reply_markup=start_to_general_kb,
    )


@router.callback_query(F.data == 'to GENERAL first time')
async def first_to_general_button(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=random_quote(),
        reply_markup=general_kb
    )


@router.callback_query(F.data == 'to GENERAL')
async def back_to_general_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text=random_quote(),
        reply_markup=general_kb
    )


@router.callback_query(F.data == 'to GENERAL from BOOK')
async def back_to_general_button(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON_RU['nice to meet you']
    )
    await callback.message.answer_animation(
        animation=LEXICON_RU['buildings_explode_gif']
    )
    await callback.message.answer(
        text=random_quote(),
        reply_markup=general_kb
    )


@router.callback_query(F.data == 'my_tasks_button IS PRESSED')
async def back_to_general_button(callback: CallbackQuery):
    active_task = await get_active_task(callback.from_user.id)

    time_ = get_time_until_next_ring(ring_time)
    if not active_task:
        await callback.answer(f'{LEXICON_RU['no_active_task']}\nДо нового: {time_}')
        return

    task_text = await get_task_text(active_task['task_id'])

    await callback.message.edit_text(
        text=f'проект РАЗГРОМ #{active_task['task_id']} {LEXICON_RU['task for now_1']}\n'
             f'{task_text}'
             f'{LEXICON_RU['task for now_2']}',
        reply_markup=tasks_kb
    )


@router.callback_query(F.data == 'task IS DONE')
async def task_is_done(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON_RU['task is done'],
        reply_markup=to_menu_kb
    )
    active_task = await get_active_task(callback.from_user.id)
    await add_completed_task(callback.from_user.id, active_task['task_id'])
    await increase_balance(callback.from_user.id, 10)
    await clear_active_task(callback.from_user.id)


@router.callback_query((F.data == 'fighter_card_button IS PRESSED') | (F.data == 'to FIGHTER_CARD'))
async def back_to_general_button(callback: CallbackQuery):
    def check_name(name):
        if type(name) == type(None):
            return ''
        else:
            return name

    username = await get_username_by_id(callback.from_user.id)
    balance = await get_balance(callback.from_user.id)
    tasks_archive = await get_completed_tasks(callback.from_user.id)

    await callback.message.edit_text(
        text=f"{LEXICON_RU['fighter_card_button']}\n\n"
             f"<code>---\n\n"
             f"Имя: {username}\n"
             f"\nБаланс: {balance} 🧼\n"
             f"\nЗаданий выполнено: {len(tasks_archive)}\n\n"
             f"---\n</code>",
        reply_markup=back_to_general_kb,
        parse_mode="HTML"
    )


async def daily_task(bot: Bot):
    print('Тайлер начинает обзвон...')

    chat_ids = await get_all_chat_ids()
    if not chat_ids:
        print("Нет chat_id для рассылки")
        return

    success = 0
    failed = 0

    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f'\t{LEXICON_RU["ring"]}',
                reply_markup=ring_kb
            )
            success += 1
        except TelegramAPIError as e:
            failed += 1
            error_msg = f"Ошибка при отправке в чат {chat_id}: "

            if "chat not found" in str(e).lower():
                error_msg += "чат не найден"
            elif "bot was blocked" in str(e).lower():
                error_msg += "бот заблокирован"
            elif "user is deactivated" in str(e).lower():
                error_msg += "пользователь деактивирован"
            else:
                error_msg += f"неизвестная ошибка: {e}"

            print(error_msg)

    print(f"Рассылка завершена. Успешно: {success}, Не удалось: {failed}")


async def check_time(time_: tuple, bot: Bot):
    while True:
        now = datetime.now()
        target_time = time(*time_)

        if now.hour == target_time.hour and now.minute == target_time.minute and now.second == target_time.second:
            await daily_task(bot)
            await asyncio.sleep(1)
        await asyncio.sleep(1)


@router.callback_query(F.data == 'ring is taken')
async def new_task_by_ring(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await is_task_given_today(user_id):
        await callback.message.delete()
        await callback.message.answer("Вы уже получили задание сегодня")
        return

    task_data = await get_random_task()
    if not task_data:
        await callback.message.delete()
        await callback.message.answer("Сейчас нет доступных заданий")
        return

    task_id, task_text, task_video = task_data

    await callback.message.delete()

    if task_video:
        sent_message = await callback.message.answer_video(
            video=task_video,
            caption='— задание дня обновлено',
            reply_markup=accept_task_kb
        )
    else:
        sent_message = await callback.message.answer(
            text=task_text,
            reply_markup=accept_task_kb
        )

    today_date = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            '''UPDATE users SET 
            active_task_id = ?,
            date_of_last_given_task = ?
            WHERE user_id = ?''',
            (task_id, today_date, user_id)
        )
        await db.commit()


@router.callback_query(F.data == 'task is ACCEPTED')
async def new_task_by_ring(callback: CallbackQuery):
    await callback.answer(
        text=LEXICON_RU['task is given'])
    await callback.message.delete()


@router.message(F.video, IsAdmin())
async def handle_new_task(message: Message):
    if not message.caption:
        await message.answer("Добавьте описание в подпись к видео!")
        return

    video_id = message.video.file_id
    task_text = message.caption

    new_task_id = await add_task(text=task_text, video_path=video_id)

    await message.answer(f"Задание добавлено! ID: {new_task_id}")


@router.message()
async def answer(message: Message):
    if message.text:
        text = random_quote(a=do_not_talk + [f'Свобода — это возможность сказать «{message.text.strip()}». '
                                             f'В такие моменты я жалею, что рабство было отменено.'])
    elif message.video or message.video_note:
        text = random_quote(a=dont_send_me_video)
    elif message.voice:
        text = random_quote(a=dont_send_me_voice)
    elif message.photo:
        text = random_quote(a=dont_send_me_photo)
    elif message.sticker:
        await message.answer_sticker(sticker=random_quote(a=sticker_pack))
    else:
        text = random_quote(a=do_not_talk)

    if not message.sticker:
        await message.answer(text=text)
