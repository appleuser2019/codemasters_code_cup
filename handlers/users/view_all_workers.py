from aiogram import types
from aiogram.dispatcher.filters import Regexp

from handlers.users.users import workers_view_menu_first
from loader import dp
from aiogram.dispatcher import FSMContext
from states.workers_view_menu import menu_move
from utils.db_api import sqlite


@dp.callback_query_handler(Regexp("come_to_view"), state=menu_move.menu)
async def back_to_view_workers(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await workers_view_menu_first(call.message, state)


@dp.callback_query_handler(Regexp("workers"), state="*")
async def workers_view_menu(call: types.CallbackQuery, state: FSMContext):
    await menu_move.menu.set()
    await call.message.delete()
    data = call.data.split("=")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Удалить сотрудника", callback_data=f"delete_worker={data[1]}"))
    worker_info = sqlite.get_worker_on_id(data[1])
    message_text = f"Имя: {worker_info[2]}\nФамилия: {worker_info[1]}\n"
    if worker_info[3] != "None":
        await state.update_data(patronymic=True)
        message_text += f"Отчество: {worker_info[3]}\n"
    else:
        await state.update_data(patronymic=False)
    message_text += f"Должность: {worker_info[4]}\nПроект: {worker_info[5]}\nДата добавления: {worker_info[7]}"

    if worker_info[6] != "None":
        await state.update_data(photo=True)
        keyboard.add(types.InlineKeyboardButton(text="Редактировать информацию",
                                                callback_data=f"redact_info={data[1]}|1"))
        keyboard.add(types.InlineKeyboardButton(text="К списку сотрудников", callback_data="come_to_view"))
        await call.message.answer_photo(caption=message_text, photo=worker_info[6], reply_markup=keyboard)
    else:
        await state.update_data(photo=False)
        keyboard.add(types.InlineKeyboardButton(text="Редактировать информацию",
                                                callback_data=f"redact_info={data[1]}|0"))
        keyboard.add(types.InlineKeyboardButton(text="К списку сотрудников", callback_data="come_to_view"))
        await call.message.answer(message_text, reply_markup=keyboard)
    await state.update_data(message=message_text, worker_id=data[1])


@dp.callback_query_handler(Regexp("redact_info"), state=menu_move.menu)
async def redacting_menu(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("=")
    data = data[1].split("|")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Изменить Имя", callback_data=f"redact_name={data[0]}"))
    keyboard.add(types.InlineKeyboardButton(text="Изменить Фамилию", callback_data=f"redact_surname={data[0]}"))
    keyboard.add(types.InlineKeyboardButton(text="Изменить Отчество", callback_data=f"redact_patronymic={data[0]}"))
    keyboard.add(types.InlineKeyboardButton(text="Изменить должность", callback_data=f"redact_post={data[0]}"))
    keyboard.add(types.InlineKeyboardButton(text="Изменить проект", callback_data=f"redact_project={data[0]}"))
    keyboard.add(types.InlineKeyboardButton(text="Изменить аватар", callback_data=f"redact_picture={data[0]}"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data[0]}"))
    data_state = await state.get_data()
    if data[1] == "1":
        await call.message.edit_caption(caption=(data_state['message'] + "\n\nВыберите, что необходимо отредактировать."), reply_markup=keyboard)
    else:
        await call.message.edit_text((data_state['message'] + "\n"
                                                              "\nВыберите, что необходимо отредактировать."), reply_markup=keyboard)


@dp.callback_query_handler(Regexp("redact_name"), state=menu_move.menu)
async def edit_name(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers{data['worker_id']}"))
    await call.message.answer("Введите новое Имя для сотрудника.", reply_markup=keyboard)
    await menu_move.edit_workers_name.set()


@dp.message_handler(state=menu_move.edit_workers_name)
async def get_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    sqlite.add_name(data['worker_id'], message.text)
    await message.answer("Вы ввели новое имя.", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("redact_surname"), state=menu_move.menu)
async def edit_surname(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers{data['worker_id']}"))
    await call.message.answer("Введите новую Фамилию для сотрудника.", reply_markup=keyboard)
    await menu_move.edit_workers_surname.set()


@dp.message_handler(state=menu_move.edit_workers_surname)
async def get_surname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    sqlite.add_surname(data['worker_id'], message.text)
    await message.answer("Вы ввели новую Фамилию.", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("redact_patronymic"), state=menu_move.menu)
async def edit_patronymic(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    if data['patronymic'] == True:
        keyboard.add(types.InlineKeyboardButton(text="Удалить Отчество", callback_data="patronymic_remove"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers{data['worker_id']}"))
    await call.message.answer("Введите новое Отчество для сотрудника.", reply_markup=keyboard)
    await menu_move.edit_workers_patronymic.set()


@dp.callback_query_handler(Regexp("patronymic_remove"), state=menu_move.edit_workers_patronymic)
async def remove_patronymic(call: types.CallbackQuery):
    await call.message.delete()
    data = call.data.split("=")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data[1]}"))
    sqlite.add_patronymic(data[1], "None")
    await call.message.answer("Вы удалили Отчество пользователя.", reply_markup=keyboard)


@dp.message_handler(state=menu_move.edit_workers_patronymic)
async def get_patronymic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    sqlite.add_patronymic(data['worker_id'], message.text)
    await message.answer("Вы ввели новое отчество.", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("redact_post"), state=menu_move.menu)
async def edit_post(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers{data['worker_id']}"))
    await call.message.answer("Введите новую должность для сотрудника.", reply_markup=keyboard)
    await menu_move.edit_workers_post.set()


@dp.message_handler(state=menu_move.edit_workers_post)
async def get_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    sqlite.add_post(data['worker_id'], message.text)
    await message.answer("Вы ввели новую должность.", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("redact_project"), state=menu_move.menu)
async def edit_project(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers{data['worker_id']}"))
    await call.message.answer("Введите новый проект для сотрудника.", reply_markup=keyboard)
    await menu_move.edit_workers_project.set()


@dp.message_handler(state=menu_move.edit_workers_project)
async def get_project(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    sqlite.add_project(data['worker_id'], message.text)
    await message.answer("Вы ввели новый проект.", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("redact_picture"), state=menu_move.menu)
async def edit_photo(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    if data['photo'] == True:
        keyboard.add(types.InlineKeyboardButton(text="Удалить аватар", callback_data=f"delete_avatar={data['worker_id']}"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    await call.message.answer("Приложите новый аватар.", reply_markup=keyboard)
    await menu_move.edit_workers_picture.set()


@dp.callback_query_handler(Regexp("delete_avatar"), state=menu_move.edit_workers_picture)
async def delete_photo(call: types.CallbackQuery):
    await call.message.delete()
    data = call.data.split("=")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data[1]}"))
    sqlite.add_picture(data[1], "None")
    await call.message.answer("Вы удалили аватар пользователя.", reply_markup=keyboard)


@dp.message_handler(state=menu_move.edit_workers_picture, content_types=['photo'])
async def get_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"workers={data['worker_id']}"))
    sqlite.add_picture(data['worker_id'], message.photo[-1].file_id)
    await message.answer("Вы выбрали новый аватар.", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("delete_worker"), state=menu_move.menu)
async def delete_worker_start(call: types.CallbackQuery):
    await call.message.delete()
    await menu_move.delete_workers.set()
    data = call.data.split("=")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Подтвердить", callback_data=f"yes={data[1]}"))
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"workers={data[1]}"))
    await call.message.answer("Вы уверены, что хотите удалить сотрудника?", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("yes"), state=menu_move.delete_workers)
async def delete_worker_finish(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = call.data.split("=")
    sqlite.delete_worker_on_id(data[1])
    await call.message.answer("Вы удалили сотрудника.")
    await state.finish()
    await workers_view_menu_first(call.message, state)
