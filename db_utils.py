# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Модуль для обработки всех запросов в БД                                                                           #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


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



if __name__ == '__main__':
    print('db_utils')
    add_chat_to_db(conn, cursor, 'Test', 1)
    add_chat_to_db(conn, cursor, 'Test', 2)
    add_chat_to_db(conn, cursor, 1, 3)
    add_chat_to_db(conn, cursor, 'Test', '2')