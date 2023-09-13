from aiogram import types
from aiogram.dispatcher.filters import Regexp

from loader import dp
from aiogram.dispatcher import FSMContext
from states.search_state import worker_start_search
from utils.db_api import sqlite


@dp.callback_query_handler(Regexp("search"))
async def search_input_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await worker_start_search.search.set()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="back"))
    data = call.data.split("=")
    if data[1] == "name":
        await call.message.answer("Введите Имя для поиска сотрудников.", reply_markup=keyboard)
        await state.update_data(format_search="name")
    elif data[1] == "surname":
        await call.message.answer("Введите Фамилию для поиска сотрудников.", reply_markup=keyboard)
        await state.update_data(format_search="surname")
    elif data[1] == "name_surname":
        await call.message.answer("Введите Фамилию и Имя через пробел для поиска сотрудников.", reply_markup=keyboard)
        await state.update_data(format_search="name_surname")
    elif data[1] == "post":
        await call.message.answer("Введите должность для поиска сотрудников.", reply_markup=keyboard)
        await state.update_data(format_search="post")
    elif data[1] == "project":
        await call.message.answer("Введите проект для поиска сотрудников.", reply_markup=keyboard)
        await state.update_data(format_search="project")


@dp.message_handler(state=worker_start_search.search)
async def searching_on_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    result = sqlite.get_workers_on_key(message.text, data['format_search'])
    if len(result) != 0:
        for i in result:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Редактировать", callback_data=f"workers={i[0]}"))
            message_text = "Вот что удалось найти:\n" \
                           f"Имя: {i[2]}\nФамилия: {i[1]}\n"
            if i[3] != "None":
                message_text += f"Отчество: {i[3]}\n"
            message_text += f"Должность: {i[4]}\nПроект: {i[5]}\nДата добавления: {i[7]}"
            if i[6] != "None":
                await message.answer_photo(caption=message_text, photo=i[6], reply_markup=keyboard)
            else:
                await message.answer(message_text, reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Закрыть", callback_data="back"))
        await message.answer("Кажется, сотрудника с такими данными не найдено...")
