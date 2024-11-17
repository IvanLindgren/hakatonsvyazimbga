import flet as ft
import time
import zipfile
import base64
from pathlib import Path
from flet_navigator import *
from utils.Buttons import Button
from PIL import Image


@route('/')
def home_page(pg: PageData) -> None:
    
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
        if sel_files:
            btn_see_photos.disabled = False
        sel_files_names.content.controls = tmp
        pg.page.update()
        
    # Выбор файла/файлов
    def pick_images(e: ft.FilePickerResultEvent) -> None:
        # Если диалоговое окно закрыто и был выбран хотя бы 1 файл
        if image_picker.result and image_picker.result.files:
            extensions = ['.png', '.jpg', '.JPG'] # Допустимые расширения
            bad_files = set() # Множество, в котором будут хранится файлы с некорректным расширением
            duplicates = set() # Множество, в котором будут хранится файлы дубликаты
            
            # Перебираем все выбранные файлы
            for file in image_picker.result.files:
                # Если файл является дубликатом, добавляем его имя в соответствующее множество
                if file.name in sel_files:
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

    # Выбор папки
    def pick_folder(e: ft.FilePickerResultEvent) -> None:
        # Перебираем каждый файл в указанной диреткории
        for file in Path(e.path).iterdir():
            # Если файл нужного формата и не является дубликатом
            if file.suffix in ['.png', '.jpg', '.JPG'] and file.name not in sel_files:
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
                sel_files[file.name] = str(Path(file)) # Добавляем файл в хеш-таблицу
                btn_see_photos.disabled = False
                btn_see_photos.update()
        
        sel_files_names.update() # Обновляем список на экране

    def pick_zip(e: ft.FilePickerResultEvent) -> None:
        # Если диалоговое окно закрыто и был выбран хотя бы 1 файл
        if zip_picker.result and zip_picker.result.files:
            
            zip = zip_picker.result.files[0]
            if Path(zip.name).suffix == '.zip':
                
                extensions = ['.png', '.jpg', '.JPG'] # Допустимые расширения
                with zipfile.ZipFile(zip.path) as zf:
                    file_names = zf.namelist()
                    
                    for file in file_names:
                        if Path(file).suffix in extensions and file not in sel_files:
                            sel_files_names.content.controls.append( 
                                ft.Text(
                                    file,
                                    size=20,
                                    color=ft.colors.WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                    width=400
                                )
                            )
                            
                            with zf.open(file) as img:
                                
                                sel_files[file] = base64.b64encode(img.read())
                                btn_see_photos.disabled = False
                                btn_see_photos.update()
            
            sel_files_names.update()

        
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
            value='Боулинг',
            color=ft.colors.WHITE,
            size=52,
            width=400,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_700,
        ),
        center_title=True,
        toolbar_height=80,
    )
    
    # Объект для обработки выбора файла/файлов
    image_picker = ft.FilePicker(on_result=pick_images)
    folder_picker = ft.FilePicker(on_result=pick_folder)
    zip_picker = ft.FilePicker(on_result=pick_zip)
    pg.page.overlay.extend([image_picker, folder_picker, zip_picker])

    # Хеш-таблица с именами файлов и путями к ним
    sel_files = dict()
    
    # Колонка с именами выбранных файлов
    sel_files_names = ft.Card(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,
            width=400,
            height=300
        )
    )

    # Создание кнопок для главной страницы
    btn_pick_image = Button(val='Изображение', page=pg.page, icon_name=ft.icons.IMAGE, height=52).create_popup_button()
    btn_pick_folder = Button(val='Папка', page=pg.page, icon_name=ft.icons.FOLDER, height=52).create_popup_button()
    btn_pick_zip = Button(val='Архив ZIP', page=pg.page, icon_name=ft.icons.ARCHIVE, height=52).create_popup_button()
    btn_see_photos = Button(val='Посмотреть фото', page=pg.page, icon_name=ft.icons.PLAY_ARROW_SHARP).create_btn()
    btn_text_choose = Button(val='Выбрать: ', page=pg.page, icon_name=ft.icons.ADD).create_btn()
    
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
    btn_text_choose.disabled = True

    # Присваиваем каждой кнопке функцию, которая будет выполняться при нажатии
    btn_pick_image.on_click = lambda _: image_picker.pick_files(allow_multiple=True)
    btn_pick_folder.on_click = lambda _: folder_picker.get_directory_path()
    btn_pick_zip.on_click = lambda _: zip_picker.pick_files()
    btn_see_photos.on_click = lambda _: pg.navigator.navigate('/viewing_photos', page=pg.page, args=list(sel_files.values()))
    btn_clear_files.on_click = clear_files

    # Объединяем в один объект колонку с именами выбранных файлов и кнопку "очистить список"
    sel_files_field = ft.Card(
        content=ft.Column([sel_files_names, btn_clear_files]), 
        shape=ft.RoundedRectangleBorder(radius=20), 
    )
    
    pb = ft.PopupMenuButton(
        content=btn_text_choose,
        items=[
            btn_pick_image,
            btn_pick_folder,
        ],
        menu_position=ft.PopupMenuPosition.UNDER,
        tooltip='Выберите нужный формат',
        
    )

    # Добавляем все созданные объекты на страницу
    pg.page.add(
        ft.Column(
            [
                btn_see_photos, pb, sel_files_field
                
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    '''btn_text_choose,
                btn_pick_image,
                btn_pick_folder,
                btn_pick_zip,
                sel_files_field,'''

