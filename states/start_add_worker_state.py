from aiogram.dispatcher.filters.state import StatesGroup, State


class start_add(StatesGroup):
    add_name = State()
    add_surname = State()
    add_patronymic = State()
    add_post = State()
    add_project = State()
    add_picture = State()
    finish = State()
