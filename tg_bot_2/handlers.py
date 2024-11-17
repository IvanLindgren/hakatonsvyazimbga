from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import logging

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import datetime
import json
import os


import keyboards as kb


router = Router()

import aiofiles

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

async def json_to_folder(players: list, json_path: str,
                         date: datetime, user_id:str, num_game:int) -> str:
    new_data = {}
    count = 0
    date_str = date.strftime('%d.%m.%Y')
    logger.info("Выполняется json_to_folder")
    # Открытие исходного файла асинхронно
    async with aiofiles.open(json_path, "r") as file:
        js_dict1 = json.loads(await file.read())

        # Обработка данных
        for item in js_dict1.items():
            if players[count] not in new_data:
                new_data[players[count]] = item[1]
            else:
                new_data[players[count] + '_2'] = item[1]
            count += 1

    # Убедимся, что директория существует
    folder_path = f'json_files/{user_id}/{date_str}'
    os.makedirs(folder_path, exist_ok=True)

    # Записываем данные в новый файл асинхронно
    file_path = f'{folder_path}/{num_game}_game.json'
    new_data_json = json.dumps(new_data, indent=4)

    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(new_data_json)



    return file_path

async def create_or_update_names_file(folder_path: str, game_data: dict, num_game: int):
    logger.info("Выполняется create_or_update_names_file")
    names_file_path = os.path.join(folder_path, "names.json")
    names_data = {}

    # Если файл уже существует, загрузим его данные
    if os.path.exists(names_file_path):
        async with aiofiles.open(names_file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            if content:
                names_data = json.loads(content)

    # Обновляем информацию для каждого игрока из game_data
    for player, scores in game_data.items():
        # Проверяем, что scores — это список
        if not isinstance(scores, list):
            continue

        # Последнее значение в списке — это финальный счёт
        final_score = scores[-1] if scores else 0
        total_points = (final_score - 100) // 30

        if player not in names_data:
            names_data[player] = {
                "GAMES": [f"GAME{num_game}"],
                "POINTS": total_points,
                "TOTAL_SCORE": final_score
            }
        else:
            names_data[player]["GAMES"].append(f"GAME{num_game}")
            names_data[player]["POINTS"] += total_points
            names_data[player]["TOTAL_SCORE"] += final_score

    # Записываем обновлённые данные обратно в names.json
    updated_names_json = json.dumps(names_data, indent=4)
    async with aiofiles.open(names_file_path, 'w', encoding='utf-8') as f:
        await f.write(updated_names_json)


def get_combined_player_stats(data_dicts):
    logger.info("Выполняется get_combined_player_stats")
    result = ""
    count = 0
    for idx, data in enumerate(data_dicts):  # Обрабатываем каждый словарь из списка
        result += f"Данные из  {idx + 1} дня:\n"  # Добавляем информацию о словаре
        for player_id, stats in data.items():
            num_games = len(stats['GAMES'])
            points = stats['POINTS']
            total_score = stats['TOTAL_SCORE']
            avg_score = total_score / num_games if num_games > 0 else 0

            result += f"  Игрок {player_id}:\n"
            result += f"    Количество игр: {num_games}\n"
            result += f"    POINTS: {points}\n"
            result += f"    TOTAL_SCORE: {total_score}\n"
            result += f"    Среднее количество очков: {avg_score:.2f}\n"
        result += "\n"  # Разделитель между словарями

    return result




async def change_rez_func(file_path:str, change_rez:list)->bool:
    logger.info("Выполняется change_rez_func")
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        content = await file.read()
        js_dict1: dict = json.loads(content)

    if change_rez[0] in js_dict1:
        js_dict1[change_rez[0]][int(change_rez[1])-1] = int(change_rez[2])
    else:
        return False

    new_data_json=json.dumps(js_dict1, indent=4)

    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(new_data_json)

    return True


def process_player_data(data: dict, players: list) -> str:
    logger.info("Выполняется process_player_data")
    new_data = {}
    count = 0

    for item in data.items():
        if players[count] not in new_data:
            new_data[players[count]] = item[1]
        else:
            new_data[players[count] + '_2'] = item[1]
        count += 1



    result = '\n'.join([f"{key}: {', '.join(map(str, value))}" for key, value in new_data.items()])

    return result


def get_player_stats(data):
    logger.info("Выполняется get_player_stats")
    result = ""
    for player_id, stats in data.items():
        num_games = len(stats['GAMES'])
        points = stats['POINTS']
        total_score = stats['TOTAL_SCORE']
        avg_score = total_score / num_games if num_games > 0 else 0

        result += f"Игрок {player_id}:\n"
        result += f"  Количество игр: {num_games}\n"
        result += f"  Очки: {points}\n"
        result += f"  Результат: {total_score}\n"
        result += f"  Среднее количество очков: {avg_score:.2f}\n\n"

    return result


# Определяем состояния для FSM
class Register(StatesGroup):
    logger.info("Выполняется get_combined_player_stats")
    photo = State()
    result = State()
    date = State()
    players = State()
    json_path = State()
    change_rez = State()
    json_file_path = State()
    user_id = State()
    num_game = State()
    generate_report_one_day_date = State()
    generate_report_several_day_date = State()


async def show_menu(event):
    await event.answer('Выберите действие:', reply_markup=kb.start_kb)


### 1. Обработчики команд

@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info("Выполняется cmd_start")
    await message.answer('Привет! Я телеграм бот для...', reply_markup=kb.menu_kb)


@router.message(Command('menu'))
async def handle_menu_command(message: Message, state: FSMContext):
    logger.info("Выполняется handle_menu_command")
    await state.clear()
    await show_menu(message)


### 2. Обработчики callback-кнопок для главного меню

@router.callback_query(F.data == 'menu')
async def handle_menu_callback(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется handle_menu_callback")
    await callback.answer()
    await state.clear()

    await callback.message.edit_reply_markup()
    await show_menu(callback.message)



@router.callback_query(F.data == 'view_data')
async def view_data(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется view_data")
    await callback.answer()
    folder_path = 'json_files'
    found_folder = False
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            found_folder = True
            break
    if found_folder:
        await callback.message.answer('Выберите вариант просмотре данных',
                                  reply_markup=kb.view_data_kb)
    else:
        await callback.message.answer('Данных пока нет',
                                      reply_markup=kb.menu_kb)

    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)


@router.callback_query(F.data.in_(['generate_report_one_day', 'generate_report_several_days']))
async def generate_report_one_day_func(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется generate_report_one_day_func")
    await callback.answer()
    result = ''
    data = await state.get_data()

    user_id = data['user_id']
    folder_path = f'json_files/{user_id}'
    folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

    for i in folders:
        result += i + '\n'

    await callback.message.answer('Вот список возможных дат:\n' + result)

    if callback.data == 'generate_report_one_day':
        await state.set_state(Register.generate_report_one_day_date)
        await callback.message.answer('Выберите дату для просмотра данных:')
    else:
        await state.set_state(Register.generate_report_several_day_date)
        await callback.message.answer('Выберите даты для просмотра данных (через пробел):')

    await callback.message.edit_reply_markup()


@router.message(Register.generate_report_several_day_date)
async def handle_player_names(message: Message, state: FSMContext):
    logger.info("Выполняется handle_player_names")
    date_in_msg = []
    list_of_dict = []
    try:
        input_user = message.text.strip().split()
        for i in input_user:
            date_in_msg.append(datetime.datetime.strptime(i, "%d.%m.%Y").date())  # Сохраняем даты в список
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
        return

    await state.update_data(generate_report_several_day_date=date_in_msg)
    data = await state.get_data()
    user_id = data['user_id']
    date = data['generate_report_several_day_date']

    for i in date:
        date_str = i.strftime('%d.%m.%Y')

        folder_path = f'json_files/{user_id}/{date_str}/names.json'
        if os.path.exists(folder_path):
            async with aiofiles.open(folder_path, "r", encoding='utf-8') as file:
                content = await file.read()
                if content:  # Проверяем, что файл не пустой
                    list_of_dict.append(json.loads(content))
                else:
                    await message.answer(f"Файл для {date_str} пуст.")
                    return
        else:
            await message.answer(f"Данные для {date_str} не внесены.")
            return

    result = get_combined_player_stats(list_of_dict)

    await message.answer(result, reply_markup=kb.menu_kb)

@router.message(Register.generate_report_one_day_date)
async def handle_player_names(message: Message, state: FSMContext):
    logger.info("Выполняется handle_player_names")
    try:
        date_in_msg = datetime.datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
        return

    await state.update_data(generate_report_one_day_date=date_in_msg)
    data = await state.get_data()
    user_id = data['user_id']
    date = data['generate_report_one_day_date']

    date_str = date.strftime('%d.%m.%Y')

    folder_path = f'json_files/{user_id}/{date_str}/names.json'
    if os.path.exists(folder_path):
        async with aiofiles.open(folder_path, "r", encoding='utf-8') as file:
            content = await file.read()
            js_dict1 = json.loads(content)
    else:
        await message.answer("Данные за эту дату не внесены.")
        return

    result = get_player_stats(js_dict1)

    await message.answer(result, reply_markup=kb.menu_kb)





### 3. Обработчики для установки имён игроков

@router.callback_query(F.data == 'set_name')
async def start_set_name(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется start_set_name")
    await callback.answer()

    await state.set_state(Register.players)

    await callback.message.answer('Напишите имена игроков (через пробел):')
    await callback.message.edit_reply_markup()


@router.message(Register.players)
async def handle_player_names(message: Message, state: FSMContext):
    logger.info("Выполняется handle_player_names")
    names = message.text.split()

    if len(names) < 2 or len(names) > 4:
        await message.answer("Пожалуйста, введите от 2 до 4 имён, разделённых пробелом.")
        return

    await state.update_data(players=names)
    data = await state.get_data()

    # Обработка данных
    players_text = ', '.join(data.get('players', []))
    date_text = data.get('date', "Дата не выбрана")

    await message.answer_photo(
        photo=data['photo'].file_id,
        caption=(
            f"Вот ваше фото.\n"
            f"Имена игроков: {players_text}\n"
            f"Дата: {date_text}"
        ),
        reply_markup=kb.photo_kb
    )

    await state.set_state(Register.photo)


### 4. Обработчики для установки даты

@router.callback_query(F.data == 'set_date')
async def start_set_date(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется start_set_date")
    await callback.answer()
    await callback.message.answer('Пожалуйста, отправьте дату в формате ДД.ММ.ГГГГ:')

    await state.set_state(Register.date)

    await callback.message.edit_reply_markup()


@router.message(Register.date)
async def handle_date(message: Message, state: FSMContext):
    logger.info("Выполняется handle_date")
    try:
        date_in_msg = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
        return

    await state.update_data(date=date_in_msg)
    data = await state.get_data()

    players_text = ', '.join(data.get('players', []))
    date_text = data['date'].strftime('%d.%m.%Y') if 'date' in data else "Дата не выбрана"

    await message.answer_photo(
        photo=data['photo'].file_id,
        caption=(
            f"Вот ваше фото.\n"
            f"Имена игроков: {players_text}\n"
            f"Дата: {date_text}"
        ),
        reply_markup=kb.photo_kb
    )

    await state.set_state(Register.photo)


### 5. Обработчики для добавления фото

@router.callback_query(F.data.in_(['change_photo', 'add_photo']))
async def add_photo(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется add_photo")
    await callback.answer()
    await state.clear()

    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(Register.photo)

    if callback.data == 'change_photo':
        await state.update_data(players=[], date=None)

    await callback.message.answer('Пришлите фото:', reply_markup=kb.menu_kb)
    await callback.message.edit_reply_markup()


@router.message(Register.photo)
async def set_photo(message: Message, state: FSMContext):
    logger.info("Выполняется set_photo")
    from main import bot
    if not message.photo:
        await message.answer("Пожалуйста, пришлите фото.")
        return

    await message.delete()
    await state.update_data(photo=message.photo[-1])

    data = await state.get_data()

    players_text = ', '.join(data.get('players', []))
    date_text = data.get('date').strftime('%d.%m.%Y') if data.get('date') else "Дата не выбрана"

    await message.answer_photo(
        photo=data['photo'].file_id,
        caption=(
            f"Вот ваше фото.\n"
            f"Имена игроков: {players_text}\n"
            f"Дата: {date_text}"
        ),
        reply_markup=kb.photo_kb
    )

    data = await state.get_data()
    photo_data = data.get('photo')
    # Получаем путь к файлу
    photo_file_info = await bot.get_file(photo_data.file_id)
    photo_file_path = photo_file_info.file_path
    photo_file = await bot.download_file(photo_file_path)

    # Убедимся, что директория существует
    folder_path = f'photos/{data['user_id']}'
    os.makedirs(folder_path, exist_ok=True)

    # Формируем путь для сохранения файла
    photo_file_name = f"{folder_path}/{photo_data.file_id}.jpg"

    async with aiofiles.open(photo_file_name, "wb") as f:
        await f.write(photo_file.read())

    # вызов модели ml с путём к фото (в зависимости от онлайн/офлайн
    # модели, будет разный вызов)
    # json_path = ml(photo_file_name)
    #  путь к JSON файлу, полученный от ML модели

    await state.update_data(json_path="../../bot_hakaton/json_from_ml/data.json")



@router.callback_query(F.data.in_(['do_calculate_offline', 'do_calculate_online']))
async def do_calculate(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется do_calculate")


    data = await state.get_data()

    if not data.get('players') or not data.get('date'):
        await callback.answer('Сначала выберите игроков и дату!', show_alert=True)
        return

    photo_data = data.get('photo')  # Делаем безопасную проверку
    if not photo_data:
        await callback.answer('Фото не выбрано!', show_alert=True)
        return



    await state.set_state(Register.num_game)

    await callback.message.answer('Напишите номер игры, под которым будут сохранены результаты...')
    await callback.message.edit_reply_markup()


@router.message(Register.num_game)
async def num_game_def(message: Message, state: FSMContext):
    logger.info("Выполняется num_game_def")
    if not message.text:
        await message.answer("Пожалуйста, пришлите номер игры.")
        return

    user_input = message.text.strip().split()
    if len(user_input) != 1:
        await message.answer("Пожалуйста, пришлите номер игры.")
        return
    elif not is_integer(user_input[0]):
        await message.answer("Пожалуйста, пришлите номер игры.")
        return

    num = int(user_input[0])
    await state.update_data(num_game=num)  # исправлено: добавлено await

    await state.set_state(Register.json_path)
    await message.answer('Отправьте любое сообщение, чтобы продолжить...')



@router.message(Register.json_path)
async def show_calculate_state(message: Message, state: FSMContext):
    logger.info("Выполняется show_calculate_state")
    data = await state.get_data()

    # Чтение содержимого JSON-файла
    try:
        if data.get('json_file_path'):
            async with aiofiles.open(data['json_file_path'], "r", encoding='utf-8') as file:
                content = await file.read()
                js_dict1 = json.loads(content)
        else:
            async with aiofiles.open(data['json_path'], "r", encoding='utf-8') as file:
                content = await file.read()
                js_dict1 = json.loads(content)


        # Проверяем, что количество имен из JSON совпадает с количеством в списке players
        if len(js_dict1) != len(data['players']):
            await message.answer("Ошибка: количество имен с изображения не совпадает с количеством имен игроков.",
                                 reply_markup=kb.menu_kb)
            return

        result = process_player_data(js_dict1, data['players'])


        await message.answer('Список игроков:\n' + result, reply_markup=kb.show_calculate_state_kb)


    except FileNotFoundError:
        await message.answer(f"Ошибка: файл {data['json_path']} не найден.",
                             reply_markup=kb.menu_kb)
        await state.clear()
    except json.JSONDecodeError:
        await message.answer("Ошибка: не удалось декодировать JSON файл.",
                             reply_markup=kb.menu_kb)
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}",
                             reply_markup=kb.menu_kb)

        await state.clear()

    if not data.get('json_file_path'):

        path = await json_to_folder(data['players'], data['json_path'],
                   data['date'], data['user_id'], data['num_game'])
        await state.update_data(json_file_path=path)





@router.callback_query(F.data == 'change_rez_players')
async def change_rez_players(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется change_rez_players")
    await state.set_state(Register.change_rez)
    await callback.answer()
    await callback.message.answer('Напишите имя игрока, номер партии (от 1 до 10),'
                                  ' в которой надо поменять кол-во очков и новое кол-во очков '
                                  '(Пример: Вася 5 50)')

@router.message(Register.change_rez)
async def change_rez_players_2(message: Message, state: FSMContext):
    user_input = message.text.strip().split()
    data = await state.get_data()


    if len(user_input) < 3 or not (is_integer(user_input[1]) and is_integer(user_input[2])):

        await message.answer('Напишите имя игрока, номер партии (от 1 до 10),'
                             ' в которой надо поменять кол-во очков и новое кол-во очков '
                             '(Пример: Вася 5 50)')
        return
    elif int(user_input[1]) < 1 or int(user_input[1]) > 10:

        await message.answer('Напишите имя игрока, номер партии (от 1 до 10),'
                                  ' в которой надо поменять кол-во очков и новое кол-во очков '
                                  '(Пример: Вася 5 50)')
        return
    success = await change_rez_func(data['json_file_path'], user_input)
    if not success:

        await message.answer('Напишите имя игрока, номер партии (от 1 до 10),'
                                  ' в которой надо поменять кол-во очков и новое кол-во очков '
                                  '(Пример: Вася 5 50)')
        return

    await state.set_state(Register.json_path)
    await message.answer('Отправьте любое сообщение, чтобы продолжить...')


@router.callback_query(F.data == 'send_json')
async def send_json(callback: CallbackQuery, state: FSMContext):
    logger.info("Выполняется send_json")
    await callback.answer()
    data = await state.get_data()
    if data.get('json_file_path'):
        file = FSInputFile(data.get('json_file_path'))
    else:
        file = FSInputFile(data.get('json_path'))

    await callback.message.answer_document(file, reply_markup=kb.menu_kb)
    await callback.message.edit_reply_markup()

    user_id = data['user_id']
    date = data['date']

    date_str = date.strftime('%d.%m.%Y')

    folder_path = f'json_files/{user_id}/{date_str}'

    num_game = data['num_game']

    if data.get('json_file_path'):
        async with aiofiles.open(data['json_file_path'], "r", encoding='utf-8') as file:
            content = await file.read()
            js_dict1 = json.loads(content)
    else:
        async with aiofiles.open(data['json_path'], "r", encoding='utf-8') as file:
            content = await file.read()
            js_dict1 = json.loads(content)

    await create_or_update_names_file(folder_path, js_dict1, num_game)


    await state.clear()



