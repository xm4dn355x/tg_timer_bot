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
from time import sleep
import threading
import psycopg2
from psycopg2.extras import DictCursor


ALERTS_LIST = []


def make_alert(timer_delay, chat_id, user, message):
    """Создает событие оповещения"""
    t = threading.Timer(timer_delay, send_alert, args=(chat_id, user, message,))
    t.start()
    return t.name


def send_alert(chat_id, user, message):
    """Мок функция для проверки работы оповещений"""
    print(f'alert: {chat_id} {user} {message} {datetime.now()}')
    thread_name = threading.current_thread().name
    pop_allert(str(thread_name))



def calculate_timer_delay(alert_time):
    """Высчитывает время до оповещения"""
    return alert_time - datetime.now()


def add_alert(time, chat_id, user, message):
    """Создает событие оповещения и добавляет его в список"""
    timer_delay = calculate_timer_delay(time)
    timer_delay = float(timer_delay.seconds)
    thread_name = make_alert(timer_delay, chat_id, user, message)
    ALERTS_LIST.append(str(thread_name))


def pop_allert(thread_name):
    ALERTS_LIST.remove(thread_name)


if __name__ == '__main__':
    print(datetime.now())
    alert_time = datetime.now() + timedelta(seconds=10)
    add_alert(alert_time, 3, 'xm4dn355x', 'hello1')
    alert_time = datetime.now() + timedelta(seconds=5)
    add_alert(alert_time, 2, 'xm4dn355x', 'hello2')
    alert_time = datetime.now() + timedelta(seconds=10)
    add_alert(alert_time, 4, 'xm4dn355x', 'hello3')
    alert_time = datetime.now() + timedelta(seconds=20)
    add_alert(alert_time, 5, 'xm4dn355x', 'hello4')
    alert_time = datetime.now() + timedelta(seconds=3)
    add_alert(alert_time, 1, 'xm4dn355x', 'hello5')
    print(datetime.now())


# id
# chat_id
# user
# time
# alerts_bot