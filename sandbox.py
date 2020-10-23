# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Скрипт для экспериментов                                                                                          #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


import logging
import re
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import DictCursor

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.request import Request

from bot_config import API_TOKEN
from bot_decorators import admin_access, log_error

import bot_timers as alerts
from db_utils import add_chat_to_db, add_curator_to_chat, add_timer_to_db, get_curators_ids, get_chat_curators_names, \
    get_chat_name_by_chat_id


# DB Connection
conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)
# cursor.execute("""SET TIMEZONE='Asia/Yekaterinburg';""")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


BUTTON_ADD_TIMER = 'Добавить таймер'
BUTTON_HELP = 'Помощь'

req = Request(connect_timeout=3)
bot = Bot(request=req, token=API_TOKEN)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher


ALERTS_TIMERS_EVENT_LOOP = alerts.run_timers_event_loop(bot=bot)


@log_error
def start_command(update: Update, context: CallbackContext):    # TODO: Добавить обработчик добавления в чат
    """Команда при добавлении бота в чат, или начала работы с ботом"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    chat_name = update.message.chat.title
    print(chat_name)
    if chat_type == 'private':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'На данный момент бот предназначен для работы исключительно в чатах',
        )
        return True
    add_chat_to_db(conn=conn, cursor=cursor, chat_name=chat_name, chat_id=chat_id)
    keyboard = [
        [
            InlineKeyboardButton('Добавить таймер', callback_data='add_timer'),
            InlineKeyboardButton('Помощь', callback_data='help'),
        ],
        [
            InlineKeyboardButton('Список кураторов', callback_data='curators_list')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text(
    #     text=f'Подключение бота к чату {chat_id}',
    #     reply_markup=reply_markup,
    # )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Подключение бота к чату {chat_id}',
        reply_markup=reply_markup,
    )


start_command_handler = CommandHandler('start', start_command)
dispatcher.add_handler(start_command_handler)


def keyboard_callback_handler(update: Update, context: CallbackContext):
    """Обработчик клавиатуры"""
    query = update.callback_query
    query.answer()
    data = query.data
    user = query.from_user
    print(user)
    username = user['username']
    user_id = user['id']
    print(f'from = {user_id} username = {username}')
    keyboard = [
        [
            InlineKeyboardButton('Добавить таймер', callback_data='add_timer'),
            InlineKeyboardButton('Помощь', callback_data='help'),
        ],
        [
            InlineKeyboardButton('Список кураторов', callback_data='curators_list')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    title = 'Шо-то там'
    if data == 'add_timer':
        print('if add timer')
        # title = 'Вы являетесь куратором данного инцидента/риска и вам необходимо следить за выполнением задачи?'
        # reply_markup = add_timer_handler()
        title = 'На какое время установить таймер? :'
        reply_markup = add_timer_date_handler()
    elif data == 'help':
        print('if help')
        title = f'Бот предназначен для проверки выполнения работы. Если вы курируете риск, или инцидент, вы можете ' \
                f'добавить в чат таймер по истечении которого бот спросит у исполнителя результат выполнения задачи и' \
                f' напишет Вам текущий статус в ЛС в виде сообщения:\n\n "Задача поставленная в чате ' \
                f'{get_chat_name_by_chat_id(chat_id=update.effective_chat.id)} успешно выполнена",\n\nлибо "Задача ' \
                f'поставленная в чате {get_chat_name_by_chat_id(chat_id=update.effective_chat.id)} НЕ выполнена" '
        reply_markup = help_handler()
    elif data == 'back_to_main':
        print('main')
        title = 'Выберите действие'
        keyboard = [
            [
                InlineKeyboardButton('Добавить таймер', callback_data='add_timer'),
                InlineKeyboardButton('Помощь', callback_data='help'),
            ],
            [
                InlineKeyboardButton('Список кураторов', callback_data='curators_list')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    # elif data == 'moder_yes':
    #     print('moder yes')
    #     title = 'Выберите срок выполнения задачи:'
    #     reply_markup = add_timer_date_handler()
    # elif data == 'moder_no':
    #     print('moder no')
    #     title = 'Только куратору/модератору следует добавлять таймеры в чат'
    #     keyboard = [
    #         [
    #             InlineKeyboardButton('Добавить таймер', callback_data='add_timer'),
    #             InlineKeyboardButton('Помощь', callback_data='help'),
    #         ],
    #         [
    #             InlineKeyboardButton('Список кураторов', callback_data='curators_list')
    #         ]
    #     ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    elif data == 'add_today' or data == 'add_tomorrow' or data == 'add_the_day_after_tomorrow' or \
            data == 'add_weekend' or data == 'add_month_end':
        title = 'Выберите время во сколько должен отгреметь таймер:'
        reply_markup = add_timer_time_handler(data)
        print('date selected')
    elif data == 'report_true':
        print('report true')
        curators_ids = get_curators_ids(chat_id=update.effective_chat.id)
        for curator_id in curators_ids:
            context.bot.send_message(
                chat_id=curator_id,
                text=f'Задача поставленная в чате {get_chat_name_by_chat_id(chat_id=update.effective_chat.id)} успешно выполнена',
            )
        title = 'Отчет направлен куратору'
        reply_markup = None
    elif data == 'report_false':
        print('report false')
        curators_ids = get_curators_ids(chat_id=update.effective_chat.id)
        for curator_id in curators_ids:
            context.bot.send_message(
                chat_id=curator_id,
                text=f'Задача поставленная в чате {get_chat_name_by_chat_id(chat_id=update.effective_chat.id)} НЕ выполнена',
            )
        title = 'Отчет направлен куратору'
        reply_markup = None
    elif data == 'curators_list':
        print('curators list')
        reply_markup = get_curators_list_markup(chat_id=update.effective_chat.id)
        if reply_markup:
            title = 'Список кураторов'
        else:
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='back_to_main')]])
            title = 'В данном чате не зарегистрирован ни один куратор'
    elif re.match(r'^\D\D\d\d\d', data):
        print(data)
        print(data[:2])
        time = get_time_from_slug(data)
        add_curator_to_chat(conn=conn, cursor=cursor, chat_id=update.effective_chat.id, user_id=user_id, username=username)
        add_timer_to_db(conn=conn, cursor=cursor, user_id=user_id, chat_id=update.effective_chat.id, time=time)
        title = f'Таймер успешно установлен на: {time}'
        reply_markup = None
    query.edit_message_text(
        text=title,
        reply_markup=reply_markup,
    )


dispatcher.add_handler(CallbackQueryHandler(keyboard_callback_handler))


# def add_timer_handler() -> InlineKeyboardMarkup:
#     keyboard = [
#         [
#             InlineKeyboardButton('Да', callback_data='moder_yes'),
#             InlineKeyboardButton('Нет', callback_data='moder_no'),
#         ]
#     ]
#     return InlineKeyboardMarkup(keyboard)


def help_handler() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('Назад', callback_data='back_to_main'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def add_timer_date_handler() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('Сегодня', callback_data='add_today'),
            InlineKeyboardButton('Завтра', callback_data='add_tomorrow'),
        ],
        [
            InlineKeyboardButton('Послезавтра', callback_data='add_the_day_after_tomorrow'),
        ],
        [
            InlineKeyboardButton('До конца недели (в разработке)', callback_data='add_weekend'),
        ],
        [
            InlineKeyboardButton('До конца месяца (в разработке)', callback_data='add_month_end'),
        ],
        [
            InlineKeyboardButton('Назад', callback_data='back_to_main'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def add_timer_time_handler(date) -> InlineKeyboardMarkup:
    if date == 'add_today':
        date_slug = 'td'
    elif date == 'add_tomorrow':
        date_slug = 'tm'
    elif date == 'add_the_day_after_tomorrow':
        date_slug = 'at'
    elif date == 'add_weekend':
        date_slug = 'we'
    elif date == 'add_month_end':
        date_slug = 'me'
    keyboard = [
        [
            InlineKeyboardButton('08:00', callback_data=f'{date_slug}080'),
            InlineKeyboardButton('08:30', callback_data=f'{date_slug}083'),
        ],
        [
            InlineKeyboardButton('09:00', callback_data=f'{date_slug}090'),
            InlineKeyboardButton('09:30', callback_data=f'{date_slug}093'),
        ],
        [
            InlineKeyboardButton('10:00', callback_data=f'{date_slug}100'),
            InlineKeyboardButton('10:30', callback_data=f'{date_slug}103'),
        ],
        [
            InlineKeyboardButton('11:00', callback_data=f'{date_slug}110'),
            InlineKeyboardButton('11:30', callback_data=f'{date_slug}113'),
        ],
        [
            InlineKeyboardButton('12:00', callback_data=f'{date_slug}120'),
            InlineKeyboardButton('12:30', callback_data=f'{date_slug}123'),
        ],
        [
            InlineKeyboardButton('13:00', callback_data=f'{date_slug}130'),
            InlineKeyboardButton('13:30', callback_data=f'{date_slug}133'),
        ],
        [
            InlineKeyboardButton('14:00', callback_data=f'{date_slug}140'),
            InlineKeyboardButton('14:30', callback_data=f'{date_slug}143'),
        ],
        [
            InlineKeyboardButton('15:00', callback_data=f'{date_slug}150'),
            InlineKeyboardButton('15:30', callback_data=f'{date_slug}153'),
        ],
        [
            InlineKeyboardButton('16:00', callback_data=f'{date_slug}160'),
            InlineKeyboardButton('16:30', callback_data=f'{date_slug}163'),
        ],
        [
            InlineKeyboardButton('17:00', callback_data=f'{date_slug}170'),
            InlineKeyboardButton('17:30', callback_data=f'{date_slug}173'),
        ],
        [
            InlineKeyboardButton('18:00', callback_data=f'{date_slug}180'),
            InlineKeyboardButton('18:30', callback_data=f'{date_slug}183'),
        ],
        [
            InlineKeyboardButton('19:00', callback_data=f'{date_slug}190'),
            InlineKeyboardButton('19:30', callback_data=f'{date_slug}193'),
        ],
        [
            InlineKeyboardButton('20:00', callback_data=f'{date_slug}200'),
            InlineKeyboardButton('20:30', callback_data=f'{date_slug}203'),
        ],
        [
            InlineKeyboardButton('21:00', callback_data=f'{date_slug}210'),
            InlineKeyboardButton('21:30', callback_data=f'{date_slug}213'),
        ],
        [
            InlineKeyboardButton('22:00', callback_data=f'{date_slug}220'),
            InlineKeyboardButton('22:30', callback_data=f'{date_slug}223'),
        ],
        [
            InlineKeyboardButton('Назад', callback_data='moder yes')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_curators_list_markup(chat_id):
    curators_names = get_chat_curators_names(chat_id=chat_id)
    print(curators_names)
    if curators_names:
        keyboard = []
        for curator in curators_names:
            keyboard.append([InlineKeyboardButton(f"""{curator['username']}""", callback_data=f"""kick{curator['user_id']}""")])
        keyboard.append([InlineKeyboardButton('Назад', callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        return reply_markup
    else:
        return None



def get_time_from_slug(slug):
    if slug[:2] == 'td':
        days = 0
    elif slug[:2] == 'tm':
        days = 1
    elif slug[:2] == 'at':
        days = 2
    elif slug[:2] == 'we':
        days = 0    # TODO: Добавить обработчик конца недели
    elif slug[:2] == 'me':
        days = 0    # TODO: Добавить обработчик конца месяца
    hours = int(slug[2:4])
    minutes = int(slug[4:] + '0')

    print(f'hours = {hours} minutes = {minutes}')
    time_now = datetime.now()
    timeshift = time_now + timedelta(
        days=days,
        hours=(hours - time_now.hour),
        minutes=(minutes - time_now.minute),
        seconds=(0 - time_now.second),
        microseconds=(0 - time_now.microsecond)
    )
    print(timeshift)
    return timeshift


@log_error
@admin_access
def start_timers(update: Update, context: CallbackContext):
    """Команда /start для запуска работы таймеров"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Таймеры запущены")
    print('START timers event loop')
    ALERTS_TIMERS_EVENT_LOOP.start()


start_timers_handler = CommandHandler('start_timers', start_timers)
dispatcher.add_handler(start_timers_handler)


@log_error
def button_add_timer_handler(update: Update, context: CallbackContext):
    bot_data = bot.get_me()
    chat_id = update.message.chat_id
    update.message.reply_text(
        text=f'Создание таймера:\nget me = {bot_data}\n\nchat id = {chat_id}',
    )


def button_help_handler(update: Update, context: CallbackContext):
    """Обработчик кнопки "Помощь"."""
    update.message.reply_text(
        text=f'Тут короче должен быть текст справки',
    )


@log_error
def main_message_handler(update: Update, context: CallbackContext):
    text = update.message.text
    print('message text:')
    print(text)
    chat_id = update.message.chat_id
    groups_list = dispatcher.groups
    print('groups list:')
    print(groups_list)

    # if text == BUTTON_ADD_TIMER:
    #     print('Добавить таймер')
    #     return button_add_timer_handler(update=update, context=context)
    #
    # if text == BUTTON_HELP:
    #     print('Помощь')
    #     return button_help_handler(update=update, context=context)

    if not text:
        # bot.send_message(
        #     text=f'Добавление в чат ID чата = {chat_id} message text = {text}',
        #     chat_id=chat_id,
        # )
        start_command(update=update, context=context)

    if text:
        update.message.reply_text(
            text=f'Сообщение боту в чат ID чата = {chat_id} message text = {text}',
        )


dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=main_message_handler))


@log_error
def user_mention_timer(update: Update, context: CallbackContext):
    """Команда /start для запуска работы таймеров"""
    mention_id = get_mention_user_id_from_message(update.message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Таки вы хотели создать таймер? Чи шо? {mention_id}")
    print('START timers event loop')
    ALERTS_TIMERS_EVENT_LOOP.start()


user_mention_timer_handler = CommandHandler('timer', user_mention_timer)
dispatcher.add_handler(user_mention_timer_handler)


def get_mention_user_id_from_message(message):
    if message.entities[0].type == 'mention':
        print('mention')

    elif message.entities[0].type == 'text_mention':
        print('text_mention')
        print()
    return 0


if __name__ == '__main__':
    updater.start_polling()
    # bot.send_message(
    #     text="[Анастасия](tg://user?id=409935891) Тест",
    #     chat_id=-478639792,
    #     parse_mode="Markdown"
    # )
    updater.idle()
