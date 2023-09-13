from aiogram.dispatcher.filters.state import StatesGroup, State


class menu_move(StatesGroup):
    menu = State()
    edit_workers_picture = State()
    edit_workers_name = State()
    edit_workers_surname = State()
    edit_workers_patronymic = State()
    edit_workers_project = State()
    edit_workers_post = State()
    delete_workers = State()