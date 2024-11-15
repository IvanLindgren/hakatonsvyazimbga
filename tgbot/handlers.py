from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import keyboards as kb

router = Router()
photo = None
players = []

# Определяем состояния
class States(StatesGroup):
    add_photo_state = State()

    set_name_state = State()

# Общая функция для обработки меню
async def show_menu(event):
    await event.answer('Выберите действие:', reply_markup=kb.start_kb)


# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        'Привет! Я телеграм бот для...',
        reply_markup = kb.menu_kb
    )

# Обработчик для команды /menu
@router.message(Command('menu'))
async def handle_menu_command(message: Message):
    await show_menu(message)

# Обработчик для нажатия на кнопку с callback_data='menu'
@router.callback_query(F.data == 'menu')
async def handle_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await show_menu(callback.message)


# Обработчик для нажатия на кнопку "add_photo"
@router.callback_query(F.data == 'add_photo')
async def add_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Пришлите фото:',
                                  reply_markup = kb.menu_kb)
    await callback.message.edit_reply_markup()
    await state.set_state(States.add_photo_state)


# Обработчик для нажатия на кнопку "view_data"
@router.callback_query(F.data == 'view_data')
async def view_data(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Данные для просмотра... (функция не дописана)')


# Обработчик для нажатия на кнопку "print_help"
@router.callback_query(F.data == 'print_help')
async def print_help(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Помощь по использованию бота... (функция не дописана)')




@router.callback_query(F.data == 'do_calculate')
async def view_data(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Данные для просмотра... (функция не дописана)')

@router.callback_query(F.data == 'set_name')
async def start_set_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Напишите имена игроков (через пробел):')
    await state.set_state(States.set_name_state)


# Обработчик для получения имён игроков
@router.message(States.set_name_state)
async def handle_player_names(message: Message, state: FSMContext):
    global players

    # Получаем текст из сообщения и разбиваем его по пробелам
    names = message.text.split()

    # Проверяем количество введённых имён
    if len(names) < 2 or len(names) > 4:
        await message.answer("Пожалуйста, введите от 2 до 4 имён, разделённых пробелом.")
        return

    # Сохраняем имена в глобальный список
    players = names
    await message.answer(f"Имена игроков сохранены: {', '.join(players)}")

    # Выходим из состояния
    await state.clear()











@router.message(States.add_photo_state)
async def set_photo(message: Message, state: FSMContext):
    global photo
    if not message.photo:
        await message.answer("Пожалуйста, пришлите фото.")
        return

    # Сохраняем фото и выходим из состояния
    photo = message.photo[-1]
    await message.answer_photo(photo=photo.file_id,
                               caption='Вот ваше фото... (функция не дописана)')
    await state.clear()


