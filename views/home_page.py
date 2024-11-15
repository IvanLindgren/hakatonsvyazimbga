import flet as ft
import time
import os
from pathlib import Path
from flet_navigator import *
from utils.Buttons import Button


@route('/')
def home_page(pg: PageData) -> None:
    
    # Поиск картинок в папке
    def search_photos(path: str) -> dict:
        photos = {}
        for file in Path(path).iterdir():
            if file.suffix in ['png', 'jpg']:
                photos[file.name] = file
        return photos
    
    # Очистка списка выбранных файлов
    def clear_files(e) -> None:
        sel_files.clear()
        sel_files_names.content.controls.clear()
        sel_files_names.update()
        btn_see_photos.disabled = True
        btn_see_photos.update()
        
    # Обработка ошибок (файлы дубликаты, некорректный формат файла)
    def error_handler(bad_files: set[str], duplicates: set[str]) -> None:
        # Временная переменаая, которая содержит список всех валидных файлов
        tmp = sel_files_names.content.controls.copy()
        
        # Перебираем все файлы с некорректным расширением
        for name in bad_files:
            # Временно сохраняем в списке название файла и причину ошибки
            sel_files_names.content.controls.append(
                ft.Text(
                        value=f"{name} - Некорректный файл",
                        size=20,
                        color=ft.colors.RED,
                        text_align=ft.TextAlign.CENTER,
                        width=400,
                        italic=True
                )
            )

        # Перебираем все файлы дубликаты
        for name in duplicates:
            # Временно сохраняем в списке название файла и причину ошибки
            sel_files_names.content.controls.append(
                ft.Text(
                        value=f"{name} - Уже добавлен",
                        size=20,
                        color=ft.colors.RED,
                        text_align=ft.TextAlign.CENTER,
                        width=400,
                        italic=True
                )
            )  
        
        # Выводим информацию о всех файлах на экран
        btn_clear_files.disabled=True
        btn_see_photos.disabled = True
        pg.page.update()
        time.sleep(2)
        
        # Спустя 2 секунду оставляем на экране список, состоящий только из валидных файлов
        btn_clear_files.disabled=False
        btn_see_photos.disabled = False
        sel_files_names.content.controls = tmp
        pg.page.update()
        
    # Выбор файла/файлов
    def pick_files(e: ft.FilePickerResultEvent) -> None:
        # Если диалоговое окно закрыто и был выбран хотя бы 1 файл
        if file_picker.result and file_picker.result.files:
            
            extensions = ['.png', 'jpg'] # Допустимые расширения
            bad_files = set() # Множество, в котором будут хранится файлы с некорректным расширением
            duplicates = set() # Множество, в котором будут хранится файлы дубликаты
            
            # Перебираем все выбранные файлы
            for file in file_picker.result.files:
                # Если файл является папкой, ищем в ней все картинки нужных форматов
                if Path(file.name).is_dir:
                    sel_files.update(search_photos(file.path))
               
                # Если файл является дубликатом, добавляем его имя в соответствующее множество
                elif file.name in sel_files:
                    duplicates.add(file.name)
                
                # Если файл имеет некорректное расширение, добавляем его имя в соответствующее множество
                elif Path(file.name).suffix not in extensions:
                    bad_files.add(file.name)
                
                else: 
                    # Добавляем имя корректного файла в список                                                               
                    sel_files_names.content.controls.append( 
                        ft.Text(
                            file.name,
                            size=20,
                            color=ft.colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                            width=400
                        )
                    )
                    
                    sel_files[file.name] = file.path  # Добавляем файл в хеш-таблицу
                    
                    btn_see_photos.disabled = False
                    btn_see_photos.update()
            
            # Если хотя бы одно множество не пустое, запускаем обработку ошибок
            if duplicates or bad_files:
                error_handler(bad_files=bad_files, duplicates=duplicates)

            sel_files_names.update() # Обновляем список на экране

    # Настройки страницы
    pg.page.title = 'Боулинг'
    pg.page.window.width = 1000
    pg.page.window.height = 700
    pg.page.window.resizable = False
    pg.page.theme_mode = ft.ThemeMode.DARK
    pg.page.vertical_alignment = ft.MainAxisAlignment.CENTER
    pg.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    #  Верхняя панель приложения
    pg.page.appbar = ft.AppBar(
        title=ft.Text(
            value='Заголовок хз',
            color=ft.colors.WHITE,
            size=52,
            width=400,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_700,
        ),
        center_title=True,
        toolbar_height=80,
        #actions=[]
    )
    
    # Объект для обработки выбора файла/файлов
    file_picker = ft.FilePicker(on_result=pick_files)
    pg.page.overlay.append(file_picker)
    
    # Хеш-таблица с именами файлов и путями к ним
    sel_files = dict()
    
    # Колонка с именами выбранных файлов
    sel_files_names = ft.Card(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,
            width=400,
            height=140
        )
    )

    # Создание кнопок для главной страницы
    btn_pick_files = Button(val='Выбрать файл', page=pg.page, icon_name=ft.icons.FOLDER).create_btn()
    btn_see_photos = Button(val='Посмотреть фото', page=pg.page, icon_name=ft.icons.PHOTO_CAMERA).create_btn()
    btn_clear_files = ft.ElevatedButton(
        text='',
        width=400,
        height=30,
        content=ft.Row(
            [
                ft.Icon(ft.icons.CLEAR, size=20, color=ft.colors.RED),
                ft.Text(
                    value='Очистить список',
                    size=20,
                    color=ft.colors.RED,
                    text_align=ft.TextAlign.CENTER
                )
            ], alignment=ft.MainAxisAlignment.START, spacing=30
        )
    )
    btn_see_photos.disabled = True

    # Присваиваем каждой кнопке функцию, которая будет выполняться при нажатии
    btn_pick_files.on_click = lambda _: file_picker.pick_files(allow_multiple=True)
    btn_see_photos.on_click = lambda _: pg.navigator.navigate('/viewing_photos', page=pg.page, args=sel_files)
    btn_clear_files.on_click = clear_files

    # Объединяем в один объект колонку с именами выбранных файлов и кнопку "очистить список"
    sel_files_field = ft.Card(
        content=ft.Column([sel_files_names, btn_clear_files]), 
        shape=ft.RoundedRectangleBorder(radius=20), 
    )
    
    # Добавляем все созданные объекты на страницу
    pg.page.add(
        ft.Column(
            [
                btn_see_photos,
                btn_pick_files,
                sel_files_field,
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    

