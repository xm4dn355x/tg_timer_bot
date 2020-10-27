# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Реализация таймеров для телеграм бота                                                                             #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


from datetime import datetime, timedelta
from time import sleep
import threading
import psycopg2
from psycopg2.extras import DictCursor
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Globals

ALERTS_LIST = []
keyboard = [
    [
        InlineKeyboardButton('Да', callback_data='report_true'),
        InlineKeyboardButton('Нет', callback_data='report_false'),
    ]
]
REPORT_MARKUP = InlineKeyboardMarkup(keyboard)

# DB Connection
conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)
cursor.execute("""SET TIMEZONE='Asia/Yekaterinburg';""")


def make_alert(id, timer_delay, bot, chat_id, message):
    """Создает событие оповещения"""
    print('make alert')
    t = threading.Timer(timer_delay, send_alert, args=(id, bot, chat_id, message))
    t.start()
    return t


def send_alert(id, bot, chat_id, message):
    """Отправка оповещения"""
    print(f'send alert: {chat_id} {message} {datetime.now()}')
    bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown") # reply_markup=REPORT_MARKUP
    pop_allert(id)
    change_alert_status_in_db(id)


def calculate_timer_delay(alert_time):
    """Высчитывает время до оповещения"""
    print('calculate timer delay')
    res = alert_time.replace(tzinfo=None) - datetime.now().replace(tzinfo=None)
    if res < timedelta(seconds=0):
        res = timedelta(seconds=5)
    return res


def add_alert(id, time, bot, chat_id, message):
    """Создает событие оповещения и добавляет его в список"""
    print('add alert')
    timer_delay = calculate_timer_delay(time)
    timer_delay = float(timer_delay.seconds)
    thread = make_alert(id, timer_delay, bot, chat_id, message)
    ALERTS_LIST.append({'id': id, 'thread': thread})


def pop_allert(id):
    """Удаляет событие оповещения из списка"""
    print('pop alert')
    for alert in ALERTS_LIST:
        if alert['id'] == id:
            ALERTS_LIST.remove(alert)


def get_alerts_list_from_db():
    """Получает список всех неотработавших таймеров"""
    print('get alerts list from db')
    cursor.execute("""SELECT id, chat_id, user_id, time FROM alerts WHERE status = FALSE""")
    try:
        res = cursor.fetchall()
    except psycopg2.ProgrammingError:
        res = []
    print(res)
    return res


def change_alert_status_in_db(id):
    """Изменяет статус таймера на отработанный в БД"""
    print('change alert status in db')
    cursor.execute(f"""UPDATE alerts SET status = TRUE WHERE id = {int(id)};""")
    conn.commit()


def run_timers_event_loop(bot):
    """Запускает ивент луп с таймерами"""
    print('init thread timers event loop')
    x = threading.Thread(target=timers_event_loop, args=(bot,))
    return x


def timers_event_loop(bot):
    """Event loop для обработки тасков с таймерами"""
    print('timers event loop')
    while True:
        alerts_list = get_alerts_list_from_db()
        for alert in alerts_list:
            add_flag = True
            for timer in ALERTS_LIST:
                if int(timer['id']) == alert['id']:
                    add_flag = False
            if add_flag:
                add_alert(
                    id=alert['id'],
                    time=alert['time'],
                    bot=bot,
                    chat_id=alert['chat_id'],
                    message=f"[Внимание!](tg://user?id={alert['user_id']}) Время на выполнение задачи подошло к концу",
                )
        sleep(5)


if __name__ == '__main__':
    print('Bot timers')
    event_loop = run_timers_event_loop()
    event_loop.start()
