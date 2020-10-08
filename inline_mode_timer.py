# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
#                                                                                                                   #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


class InlineTimerSetter:

    def __init__(self, chat_id: int, time: int):
        """Инициализация класса"""
        self.chat_id = chat_id
        self.time = time

    def parse_query(self, text: str) -> list:
        """Понять что пользователь пишет"""
        val = text.strip()
        try:
            val = int(val)
        except ValueError:
            return 'Введите число (количество минут)'
        return val

    def set_timer(self, chat_id: int, time: int):
        """Создание таймера по запросу"""
        print(f'chat_id = {chat_id}, time = {time}')
        print('Допустим создали таймер в базе')


if __name__ == '__main__':
    pass
