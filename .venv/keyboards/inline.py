from aiogram.types import (KeyboardButton, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove,
                           KeyboardButtonPollType, InlineKeyboardButton,
                           InlineKeyboardMarkup, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from lexicon.lexicon import LEXICON_RU

####################################################################

start_game_button = InlineKeyboardButton(
    text=LEXICON_RU['start_game_button'],
    callback_data='start game'
)

start_kb = InlineKeyboardMarkup(
    inline_keyboard=[[start_game_button]]
)

####################################################################
'''General Screen keyboard. Includes My_Tasks, Fighter_Card'''

my_tasks_button = InlineKeyboardButton(
    text=LEXICON_RU['my_tasks_button'],
    callback_data='my_tasks_button IS PRESSED'
)

fighter_card_button = InlineKeyboardButton(
    text=LEXICON_RU['fighter_card_button'],
    callback_data='fighter_card_button IS PRESSED'
)

general_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [my_tasks_button],
        [fighter_card_button]
    ]
)

#####################################################################

back_to_general = InlineKeyboardButton(
    text='<<<',
    callback_data='to GENERAL'
)

back_to_general_kb = InlineKeyboardMarkup(
    inline_keyboard=[[back_to_general]]
)

#####################################################################

ok_button = InlineKeyboardButton(
    text=LEXICON_RU['OK'],
    callback_data='to GENERAL first time'
)

start_to_general_kb = InlineKeyboardMarkup(
    inline_keyboard=[[ok_button]]
)

######################################################################

task_is_done = InlineKeyboardButton(
    text='✅',
    callback_data='task IS DONE'
)

tasks_kb = InlineKeyboardMarkup(
    inline_keyboard=[[task_is_done],
                     [back_to_general]]
)

######################################################################

to_menu = InlineKeyboardButton(
    text=LEXICON_RU['to_menu'],
    callback_data='to GENERAL'
)

to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[to_menu]]
)

#######################################################################
'''THIS IS THE PART WHERE WE DESCRIBE DAILY NOTIFICATION ABOUT NEW TASK'''

take_ring_button = InlineKeyboardButton(
    text=LEXICON_RU['pick up'],
    callback_data='ring is taken'
)

ring_kb = InlineKeyboardMarkup(
    inline_keyboard=[[take_ring_button]]
)

task_is_accepted = InlineKeyboardButton(
    text='Принято',
    callback_data='task is ACCEPTED'
)

accept_task_kb = InlineKeyboardMarkup(
    inline_keyboard=[[task_is_accepted]]
)
