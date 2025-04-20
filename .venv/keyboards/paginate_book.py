from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

CHARS_PER_PAGE = 500
HEAD = '''📜 <code>ПРОТОКОЛ «РАЗГРОМ»</code>\n
<code>-----------------------</code>\n'''
DOWN = '''\n<code>-----------------------</code>'''

TEXT = '''
<b>Как это работает?</b>

Каждый день в одно и то же время тебе будет приходить сообщение-звонок:

<code>(⁽⁽☎️⁾⁾) Вызов от Тайлера</code>

— в котором Тайлер назовёт твоё задание на сегодня.\n\nНе приказ, не ультиматум — просто вызов. Ты можешь его выполнить. Или не выполнить. Это твой выбор, твоя ответственность, твоя слабость.

Система не будет давить на тебя — она лишь покажет дверь. Войти или остаться снаружи — решаешь только ты. Но знай: каждый пропущенный вызов — это не поражение системы, а твоя личная капитуляция.\n\nТы делаешь это не для бота, не для баллов, а для себя. Вернее, для того, кем ты мог бы стать, если бы перестал ныть и начал действовать.

<code>«Ну ма-а-ам, ну пожалуйста, не говори Тайлеру Дёрдену, что я не доел кашу...»</code>

В общем, если выполнишь задание (или хотя бы сделаешь вид) - нажимай на жирную такую галочку в разделе заданий. После этого твой мыльный баланс пополнится.

А на следующий день — новое задание. И так до тех пор, пока ты не поймёшь, что больше не боишься того, чего боялся раньше...

<b>Где следить за прогрессом:</b>\n
Загляни в «Карточку бойца» — там твой баланс мыла и жестокое напоминание о том, как тебя назвали при рождении. Родители явно были не в себе.

<b>Зачем нужно мыло?</b>
Чтобы отмываться от стыда за невыполненные задания!
Понимаю, маленький любитель Бойцовского клуба, ты редко принимаешь душ, но гигиена — это не про слабость, это про контроль. Даже Тайлер Дёрден чистил зубы. Иногда.

<i>Ты здесь не для развлечения. Ты здесь, чтобы сломать то, что мешает тебе быть свободным.</i>
'''


def split_text(text: str, max_chars: int) -> list[str]:
    """Разбивает текст на страницы по количеству символов, обрывая только на двойных переносах"""
    pages = []
    current_page = ""
    paragraphs = text.strip().split('\n\n')

    for para in paragraphs:
        if len(current_page) + len(para) + 2 <= max_chars:
            current_page += para + "\n\n"
        else:
            if current_page:
                pages.append(current_page.strip())
            current_page = para + "\n\n"

    if current_page:
        pages.append(current_page.strip())
    return pages


text_pages = split_text(TEXT, CHARS_PER_PAGE)


def build_page(page_num: int) -> tuple[str, InlineKeyboardBuilder]:
    """Создает текст страницы и клавиатуру"""
    page_num = max(0, min(page_num, len(text_pages) - 1))
    page_content = f"{HEAD}\n{text_pages[page_num]}\n{DOWN}"

    builder = InlineKeyboardBuilder()

    prev_data = "no_action" if page_num == 0 else f"page_{page_num - 1}"
    builder.button(text="<<", callback_data=prev_data)

    builder.button(text=f"{page_num + 1}/{len(text_pages)}", callback_data="no_action")

    next_data = "no_action" if page_num == len(text_pages) - 1 else f"page_{page_num + 1}"
    builder.button(text=">>", callback_data=next_data)
    builder.button(text="В меню", callback_data='to GENERAL from BOOK')

    builder.adjust(3, 1)

    return page_content, builder
