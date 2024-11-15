import flet as ft
import time
from pathlib import Path
from flet_navigator import *
from utils.Buttons import Button


@route('/viewing_photos')
def viewing_photos(pg: PageData) -> None:
    
    # Получаем фото с прошлой страницы
    sel_files = pg.arguments
    
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
            value='Заголовок 2 хз',
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

    


   
    
    
    
    

