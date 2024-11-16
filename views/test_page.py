import flet as ft
from flet_navigator import *


@route('/test')
def test(pg: PageData) -> None:
    pg.page.title = 'Боулинг'
    pg.page.window.width = 1000
    pg.page.window.height = 700
    pg.page.window.resizable = False
    pg.page.theme_mode = ft.ThemeMode.DARK
    pg.page.vertical_alignment = ft.MainAxisAlignment.CENTER
    pg.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    