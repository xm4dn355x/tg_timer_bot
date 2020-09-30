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


# DB Connection
conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)
# cursor.execute("""SET TIMEZONE='Asia/Yekaterinburg';""")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


BUTTON_HELP = 'Помощь'

req = Request(connect_timeout=3)
bot = Bot(request=req, token=API_TOKEN)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher


def log_error(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'ERROR: {e}')
            raise e
    return inner


@log_error
def start(update, context):
    """Команда /start"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


@log_error
def button_help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        text='Раздел помощь',
        reply_markup=ReplyKeyboardRemove(),
    )


@log_error
def test_message_handler(update: Update, context: CallbackContext):
    text = update.message.text

    if text == BUTTON_HELP:
        print('ПОМОЩЬ')
        return button_help_handler(update=update, context=context)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BUTTON_HELP)
            ],
        ],
        resize_keyboard=True,
    )

    update.message.reply_text(
        text='Йо! тестовое сообщение!',
        reply_markup=reply_markup,
    )

dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=test_message_handler))


if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
