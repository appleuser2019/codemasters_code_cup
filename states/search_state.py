from aiogram.dispatcher.filters.state import StatesGroup, State


class worker_start_search(StatesGroup):
    search = State()
