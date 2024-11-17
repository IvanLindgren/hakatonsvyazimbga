from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton

state_num: int = 0


photo_kb = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text='Выполнить расчет (online)', callback_data='do_calculate_online')],
[InlineKeyboardButton(text='Выполнить расчет (offline)', callback_data='do_calculate_offline')],
[InlineKeyboardButton(text='Добавить/Изменить имена', callback_data='set_name')],
[InlineKeyboardButton(text='Добавить/Изменить дату', callback_data='set_date')],
[InlineKeyboardButton(text='Изменить фото', callback_data='change_photo')],
[InlineKeyboardButton(text='Выйти', callback_data='menu')]
])

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')],
    [InlineKeyboardButton(text='Посмотреть данные', callback_data='view_data')]
])

menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Меню", callback_data="menu")]
])

show_calculate_state_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить", callback_data="change_rez_players")],
[InlineKeyboardButton(text="Отправить json и выйти", callback_data="send_json")]
])

view_data_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="За один день", callback_data="generate_report_one_day")],
[InlineKeyboardButton(text="За несколько дней", callback_data="generate_report_several_days")]
])


