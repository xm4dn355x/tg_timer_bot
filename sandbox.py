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

conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)
cursor.execute("""SET TIMEZONE='Asia/Yekaterinburg';""")


def make_alert(id, timer_delay, chat_id, message):
    """Создает событие оповещения"""
    t = threading.Timer(timer_delay, send_alert, args=(id, chat_id, message,))
    t.start()
    return t


def send_alert(id, chat_id, message):
    """Отправка оповещения"""
    print(f'alert: {chat_id} {message} {datetime.now()}')
    pop_allert(id)
    change_alert_status_in_db(id)
    print(ALERTS_LIST)


def calculate_timer_delay(alert_time):
    """Высчитывает время до оповещения"""
    res = alert_time.replace(tzinfo=None) - datetime.now().replace(tzinfo=None)
    if res < timedelta(seconds=0):
        res = timedelta(seconds=5)
    print(res)
    return res


def add_alert(id, time, chat_id, message):
    """Создает событие оповещения и добавляет его в список"""
    timer_delay = calculate_timer_delay(time)
    timer_delay = float(timer_delay.seconds)
    thread = make_alert(id, timer_delay, chat_id, message)
    ALERTS_LIST.append({'id': id, 'thread': thread})


def pop_allert(id):
    """Удаляет событие оповещения из списка"""
    for alert in ALERTS_LIST:
        if alert['id'] == id:
            ALERTS_LIST.remove(alert)


def generate_message(username):
    return f"@{username} Обратный отсчет окончен. Отчитайтесь пожалуйста"


def get_alerts_list_from_db():
    cursor.execute("""SELECT id, chat_id, username, time FROM alerts WHERE status = FALSE""")
    return cursor.fetchall()


def change_alert_status_in_db(id):
    cursor.execute(f"""UPDATE alerts SET status = TRUE WHERE id = {int(id)};""")
    conn.commit()


def run_timers_event_loop():
    """Запускает ивент луп"""
    x = threading.Thread(target=timers_event_loop)
    return x


def timers_event_loop():
    while True:
        alerts_list = get_alerts_list_from_db()
        for alert in alerts_list:
            add_flag = True
            for timer in ALERTS_LIST:
                if int(timer['id']) == alert['id']:
                    add_flag = False
            if add_flag == True:
                add_alert(
                    id=alert['id'],
                    time=alert['time'],
                    chat_id=alert['chat_id'],
                    message=generate_message(alert['username'])
                )
            else:
                print('Alert in list')
        print(ALERTS_LIST)
        sleep(5)



if __name__ == '__main__':
    event_loop = run_timers_event_loop()
    event_loop.start()


# id
# chat_id
# user
# time
# status