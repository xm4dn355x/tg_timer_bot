# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Скрипт для экспериментов                                                                                          #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


from datetime import datetime
from datetime import timedelta
import threading
import psycopg2
from psycopg2.extras import DictCursor


ALERTS_LIST = []

conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)
cursor.execute("""SET TIMEZONE='Asia/Yekaterinburg';""")


def make_alert(id, timer_delay, chat_id, user, message):
    """Создает событие оповещения"""
    t = threading.Timer(timer_delay, send_alert, args=(id, chat_id, user, message,))
    t.start()
    return t.name


def send_alert(id, chat_id, user, message):
    """Мок функция для проверки работы оповещений"""
    print(f'alert: {chat_id} {user} {message} {datetime.now()}')
    thread_name = threading.current_thread().name
    pop_allert(id, thread_name)



def calculate_timer_delay(alert_time):
    """Высчитывает время до оповещения"""
    res = alert_time.replace(tzinfo=None) - datetime.now().replace(tzinfo=None)
    if res < timedelta(seconds=0):
        res = timedelta(seconds=5)
    print(res)
    return res


def add_alert(id, time, chat_id, user, message):
    """Создает событие оповещения и добавляет его в список"""
    timer_delay = calculate_timer_delay(time)
    timer_delay = float(timer_delay.seconds)
    thread_name = make_alert(id, timer_delay, chat_id, user, message)
    ALERTS_LIST.append({'id': id, 'thread_name': str(thread_name)})


def pop_allert(id, thread_name):
    ALERTS_LIST.remove({'id': id, 'thread_name': thread_name})


def get_alerts_list_from_db():
    cursor.execute("""SELECT id, chat_id, username, time FROM alerts WHERE status = FALSE""")
    return cursor.fetchall()


if __name__ == '__main__':
    alerts_list = get_alerts_list_from_db()
    for alert in alerts_list:
        add_alert(
            id=alert['id'],
            time=alert['time'],
            chat_id=alert['chat_id'],
            user=alert['username'],
            message='Hello Bitch!'
        )

    # TODO: реализовать выключение потоков скорей всего добавлять в список потоки и потом прогоняться по имено и закрывать
    # TODO: ебануть управление через бота


# id
# chat_id
# user
# time
# status