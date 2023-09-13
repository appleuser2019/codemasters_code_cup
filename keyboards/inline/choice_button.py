import os

from aiogram import types



from data.strings import *
from utils.db_api import sqlite

user_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_keyboard.row("Добавить сотрудника")
user_keyboard.row("Просмотр сотрудников", "Поиск сотрудника")

CLOSE_BTN = types.InlineKeyboardButton(text="Закрыть", callback_data="close")

cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.row("Отмена")


def get_keyboard_for_finish(user_id):
    """
    Получение клавиатуры после завершения действия

    :param user_id: user id
    :return:
    """

    return user_keyboard


def create_list_keyboard(data, last_index, page_click: str, btn_text_param, btn_click, back_method=None):
    """
    Создание страничной клавиатуры

    :param data: данные для клавиатуры
    :param last_index: послендий индекс
    :param page_click: метод для нажатия вперед/назад
    :param btn_text_param: текст для кнопки
    :param btn_click: метод для кнопки
    :param back_method: метод для кнопки назад, по умолчанию None
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()
    btn_list = []

    btn_text = ""

    if page_click.endswith("="):
        callback = f"{page_click}"
    else:
        callback = f"{page_click}|"

    if last_index >= 10:
        btn_list.append(types.InlineKeyboardButton(
            text="Назад", callback_data=f"{callback}{(last_index - 10)}"
        ))

    if len(data) > 0:
        limit = last_index + 10

        while last_index < limit and last_index < len(data):
            click = f"{btn_click}={data[last_index][0]}"

            if btn_text_param == "support":
                btn_text = f"#{data[last_index][0]} | {data[last_index][1]}"
            elif btn_text_param == "user_support":
                btn_text = f"#{data[last_index][0]}"

            keyboard.add(
                types.InlineKeyboardButton(text=btn_text,
                                           callback_data=click)
            )
            last_index += 1

        if last_index < len(data):
            btn_list.append(types.InlineKeyboardButton(
                text="Далее", callback_data=f"{callback}{last_index}"
            ))

        keyboard.row(*btn_list)

    if back_method is not None:
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data=back_method))
    keyboard.add(CLOSE_BTN)

    return keyboard



def create_workers_keyboard(method_item):
    """
    Создание клавиатуры с подкатегориями и товарами в категории

    :param category_id: id категории
    :param method_subcategory: метод категории для callback_data
    :param method_item: метод товара для callback_data
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()
    items = sqlite.get_all_workers()
    for i in range(len(items)):
        keyboard.add(types.InlineKeyboardButton(
            text=workers_format(items[i]),
            callback_data=f"{method_item}={items[i][0]}"
        ))
    return keyboard
