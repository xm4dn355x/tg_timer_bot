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


def log_error(f):
    """Отлавливание ошибок"""
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'ERROR: {e}')
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
    pass