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
import psycopg2
from psycopg2.extras import DictCursor

from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.request import Request

from bot_config import API_TOKEN
from bot_decorators import admin_access, log_error

import bot_timers as alerts


# DB Connection
conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)
# cursor.execute("""SET TIMEZONE='Asia/Yekaterinburg';""")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


BUTTON_ADD_TIMER = 'Добавить таймер'

req = Request(connect_timeout=3)
bot = Bot(request=req, token=API_TOKEN)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher


ALERTS_TIMERS_EVENT_LOOP = alerts.run_timers_event_loop(bot=bot)


@log_error
@admin_access
def start_timers(update: Update, context: CallbackContext):
    """Команда /start для запуска работы таймеров"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Таймеры запущены")
    print('START timers event loop')
    ALERTS_TIMERS_EVENT_LOOP.start()


start_handler = CommandHandler('start', start_timers)
dispatcher.add_handler(start_handler)


@log_error
def button_add_timer_handler(update: Update, context: CallbackContext):
    bot_data = bot.get_me()
    chat_id = update.message.chat_id
    update.message.reply_text(
        text=f'Создание таймера:\nget me = {bot_data}\n\nchat id = {chat_id}',
        reply_markup=ReplyKeyboardRemove(),
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

    if text == BUTTON_ADD_TIMER:
        print('Добавить таймер')
        return button_add_timer_handler(update=update, context=context)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BUTTON_ADD_TIMER)
            ],
        ],
        resize_keyboard=True,
    )
    if not text:
        bot.send_message(
            text=f'Добавление в чат ID чата = {chat_id} message text = {text}',
            chat_id=chat_id,
        )
    if text:
        update.message.reply_text(
            text=f'Сообщение боту в чат ID чата = {chat_id} message text = {text}',
            reply_markup=ReplyKeyboardRemove(),
        )


dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=main_message_handler))


if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
