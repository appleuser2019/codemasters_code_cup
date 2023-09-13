from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from states.start_add_worker_state import start_add
from utils.db_api import sqlite
from datetime import date


@dp.callback_query_handler(Regexp("start_add"), state='*')
async def start_add_worker(call: types.CallbackQuery):
    await call.message.delete()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await call.message.answer("Необязательные пункты Вы можете пропустить, нажав кнопку 'Пропустить'.\n"
                              "\nВведите Имя сотрудника", reply_markup=keyboard)
    await start_add.add_name.set()


@dp.message_handler(state=start_add.add_name)
async def add_surname(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await state.update_data(name=message.text)
    await start_add.add_surname.set()
    await message.answer("Введите Фамилию сотрудника", reply_markup=keyboard)


@dp.message_handler(state=start_add.add_surname)
async def add_patronymic(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="skip"))
    await state.update_data(surname=message.text)
    await start_add.add_patronymic.set()
    await message.answer("Введите Отчество сотрудника.\nВы можете пропустить этот пункт, нажав 'Пропустить'.",
                         reply_markup=keyboard)


@dp.callback_query_handler(Regexp("skip"), state=start_add.add_patronymic)
async def add_patronymic_skip(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await state.update_data(patronymic="None")
    await add_post_start(call.message)


@dp.message_handler(state=start_add.add_patronymic)
async def patronymic_not_skip(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await state.update_data(patronymic=message.text)
    await add_post_start(message)


async def add_post_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await start_add.add_post.set()
    await message.answer("Введите должность сотрудника.", reply_markup=keyboard)


@dp.message_handler(state=start_add.add_post)
async def add_project(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await state.update_data(post=message.text)
    await start_add.add_project.set()
    await message.answer("Введите проект сотрудника.", reply_markup=keyboard)


@dp.message_handler(state=start_add.add_project)
async def add_picture(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="skip"))
    await state.update_data(project=message.text)
    await start_add.add_picture.set()
    await message.answer("Прикрепите аватарку сотруднику. Данный шаг можно пропустить", reply_markup=keyboard)


@dp.message_handler(content_types=['photo'], state=start_add.add_picture)
async def add_picture_not_skip(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    await start_add.finish.set()
    await ending_message(message, state)


@dp.callback_query_handler(Regexp("skip"), state=start_add.add_picture)
async def add_photo_skip(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(photo="None")
    await start_add.finish.set()
    await ending_message(call.message, state)


async def ending_message(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Завершить", callback_data="end_adding"))
    keyboard.add(types.InlineKeyboardButton(text="Заполнить заново", callback_data="start_add"))
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="back"))
    data = await state.get_data()
    message_text = "Проверьте правильность заполнения:\n" \
                   f"Имя: {data['name']}\nФамилия: {data['surname']}\n"

    if data['patronymic'] != "None":
        message_text += f"Отчество: {data['patronymic']}\n"
    message_text += f"Должность: {data['post']}\nПроект: {data['project']}"

    if data['photo'] != "None":
        await message.answer_photo(caption=message_text, photo=data['photo'], reply_markup=keyboard)
    else:
        await message.answer(message_text, reply_markup=keyboard)


@dp.callback_query_handler(Regexp("end_adding"), state=start_add.finish)
async def end_add_worker(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(date=date.today())
    data = await state.get_data()
    sqlite.add_worker(data)
    await state.finish()
    await call.message.answer("Вы успешно добавили сотрудника.")
