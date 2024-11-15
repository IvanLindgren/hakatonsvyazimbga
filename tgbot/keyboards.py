from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton

labels_for_photo = [
InlineKeyboardButton(text='Выполнить расчет', callback_data='do_calculate'),
InlineKeyboardButton(text='Добавить имена участникам', callback_data='set_name'),
InlineKeyboardButton(text='Выбрать дату', callback_data='set_date'),
InlineKeyboardButton(text='Изменить имена', callback_data='set_name'),
InlineKeyboardButton(text='Изменить фото', callback_data='set_photo'),
InlineKeyboardButton(text='Изменить дату', callback_data='set_date'),
InlineKeyboardButton(text='Выйти', callback_data='menu'),
]

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')],
    [InlineKeyboardButton(text='Посмотреть данные', callback_data='view_data')],
    [InlineKeyboardButton(text='Помощь(/help)', callback_data='print_help')],
])

menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Меню", callback_data="menu")]
])