from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from keyboards.inline import choice_button
from utils.db_api import sqlite
from keyboards.inline.choice_button import user_keyboard


@dp.callback_query_handler(regexp="back", state="*")
async def back_message_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    keyboard = user_keyboard

    await call.message.answer("🔹 Главное меню 🔹\nВыберите необходимое действие.", reply_markup=keyboard)


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = user_keyboard
    message_text = sqlite.get_param("hello_message").format(username=message.chat.username)
    await message.answer(message_text, reply_markup=keyboard)


@dp.message_handler(regexp="Добавить сотрудника", state="*")
async def add_worker(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Начать", callback_data="start_add"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    await message.answer("Вы хотите начать процесс добавления сотрудника?", reply_markup=keyboard)


@dp.message_handler(regexp="Просмотр сотрудников", state="*")
async def workers_view_menu_first(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = choice_button.create_workers_keyboard("workers")
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="back"))
    await message.answer("Выберите необходимого сотрудника"
                         " для вывода или редактирования информации.", reply_markup=keyboard)


@dp.message_handler(regexp="Поиск сотрудника", state="*")
async def search_worker_menu(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Имя", callback_data="search=name"))
    keyboard.add(types.InlineKeyboardButton(text="Фамилия", callback_data="search=surname"))
    keyboard.add(types.InlineKeyboardButton(text="Имя и Фамилия", callback_data="search=name_surname"))
    keyboard.add(types.InlineKeyboardButton(text="Должность", callback_data="search=post"))
    keyboard.add(types.InlineKeyboardButton(text="Проект", callback_data="search=project"))
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="back"))
    await message.answer("Выберите способ поиска из списка ниже:", reply_markup=keyboard)
