import flet as ft
from flet_navigator import *


@route('/statistics_page')
def statistics_page(pg: PageData) -> None:
    pg.page.title = 'Статистика'
    pg.page.window.width = 1000
    pg.page.window.height = 700
    pg.page.window.resizable = False
    pg.page.theme_mode = ft.ThemeMode.DARK
    pg.page.vertical_alignment = ft.MainAxisAlignment.CENTER
    pg.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    btn_go_home = ft.IconButton(
        icon=ft.icons.HOME,
        icon_size=52,
        icon_color=ft.colors.WHITE,
        tooltip='На главную',
        on_click=lambda _: pg.navigator.navigate('/', page=pg.page)
    )
    
    pg.page.appbar = ft.AppBar(
        title=ft.Text(
            value='Статистика',
            color=ft.colors.WHITE,
            size=52,
            width=400,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_700,
        ),
        center_title=True,
        toolbar_height=80,
        actions=[btn_go_home]
    )

    