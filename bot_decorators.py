# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Декораторы для телеграм бота                                                                                      #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


ADMIN_IDS = [
    126423831,
]
MODERATOR_IDS = [
    126423831,
]
MAIN_ADMIN_ID = 126423831


def log_error(f):
    """Отлавливание ошибок"""
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error = f'ERROR {e} in '
            print(error)
            update = args[0]
            if update and hasattr(update, 'message'):
                update.message.bot.send_message(chat_id=MAIN_ADMIN_ID, text=error)
            raise e
    return inner


def admin_access(f):
    """Доступ только админа"""
    def inner(*args, **kwargs):
        update = args[0]
        if update and hasattr(update, 'message'):
            chat_id = update.message.chat_id
            if chat_id in ADMIN_IDS:
                return f(*args, **kwargs)
    return inner


def moderator_access(f):
    def inner(*args, **kwargs):
        update = args[0]
        if update and hasattr(update, 'message'):
            chat_id = update.message.chat_id
            if chat_id in MODERATOR_IDS:
                return f(*args, **kwargs)

    return inner
