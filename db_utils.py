# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Модуль для обработки всех запросов в БД                                                                           #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import DictCursor


conn = psycopg2.connect(dbname='alerts_bot', user='alerts_bot', password='alerts_bot', host='localhost')
cursor = conn.cursor(cursor_factory=DictCursor)


def add_chat_to_db(conn: psycopg2.connect, cursor, chat_name: str, chat_id: int):
    """Добавляет чат в список чатов. Если чат уже есть в БД, то возвращает False"""
    cursor.execute(f"""SELECT * FROM chats WHERE chat_id = {int(chat_id)}""")
    chat = cursor.fetchone()
    if not chat:
        cursor.execute(f"""INSERT INTO chats (chat_name, chat_id) VALUES ('{chat_name}', {int(chat_id)})""")
        conn.commit()


def add_timer_to_db(conn: psycopg2.connect, cursor, chat_id: int, time: datetime):
    print('add_timer_to_db')
    time = time - timedelta(hours=5)
    cursor.execute(f"""INSERT INTO alerts (chat_id, time) VALUES ({chat_id}, '{time}')""")
    conn.commit()


def add_curator_to_chat(conn: psycopg2.connect, cursor, chat_id: int, user_id: int, username: str):
    print('add_curator_to_chat')
    cursor.execute(f"""SELECT user_id FROM curators WHERE chat_id = {chat_id}""")
    rows = cursor.fetchall()
    print(chat_id)
    print(user_id)
    print(rows)
    is_in_db = False
    if rows:
        for row in rows:
            print(row)
            if row['user_id'] == user_id:
                print('USER id in DB!')
                is_in_db = True
    if is_in_db == False:
        cursor.execute(f"""INSERT INTO curators (chat_id, user_id, username) VALUES ({chat_id}, {user_id}, '{username}')""")
        conn.commit()


def get_curators_ids(chat_id):
    cursor.execute(f"""SELECT user_id FROM curators WHERE chat_id = {chat_id}""")
    rows = cursor.fetchall()
    curators = []
    for row in rows:
        curators.append(row['user_id'])
    return curators


def get_chat_name_by_chat_id(chat_id):
    cursor.execute(f"""SELECT chat_name FROM chats WHERE chat_id = {chat_id}""")
    res = cursor.fetchone()
    return res['chat_name']


def get_chat_curators_names(chat_id: int) -> list:
    cursor.execute(f"""SELECT user_id, username FROM curators WHERE chat_id = {chat_id}""")
    res = cursor.fetchall()
    return res


if __name__ == '__main__':
    print('db_utils')
    add_chat_to_db(conn, cursor, 'Test', 1)
    add_chat_to_db(conn, cursor, 'Test', 2)
    add_chat_to_db(conn, cursor, 1, 3)
    add_chat_to_db(conn, cursor, 'Test', '2')