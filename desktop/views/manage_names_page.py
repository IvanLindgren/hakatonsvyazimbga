import flet as ft
from flet_navigator import *
from desktop.alghorithm_desktop import ml_alg


@route('/manage_names_page')
def manage_names_page(pg: PageData) -> None:
    
    def set_name(e) -> None:
        pass

    print(pg.arguments)
    
    pg.page.title = 'Управление именами игроков'
    pg.page.window.width = 1000
    pg.page.window.height = 700
    pg.page.window.resizable = False
    pg.page.theme_mode = ft.ThemeMode.DARK
    pg.page.vertical_alignment = ft.MainAxisAlignment.CENTER
    pg.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    names = {'p1': None, 'p2': None, 'p3': None, 'p4': None}

    input_player1 = ft.TextField(label='Имя 1:', width=600, height=80, on_submit=lambda _: names.update({'p1': input_player1.value}))
    input_player2 = ft.TextField(label='Имя 2:', width=600, height=80, on_submit=lambda _: names.update({'p2': input_player2.value}))
    input_player3 = ft.TextField(label='Имя 3:', width=600, height=80, on_submit=lambda _: names.update({'p3': input_player3.value}))
    input_player4 = ft.TextField(label='Имя 4:', width=600, height=80, on_submit=lambda _: names.update({'p4': input_player4.value}))
    
    col = ft.Column([input_player1, input_player2, input_player3, input_player4])
    
    btn_go_home = ft.IconButton(
        icon=ft.icons.HOME,
        icon_size=52,
        icon_color=ft.colors.WHITE,
        tooltip='На главную',
        on_click=lambda _: pg.navigator.navigate('/', page=pg.page)
    )

    btn_go_statistics = ft.IconButton(
        icon=ft.icons.PLAY_ARROW_SHARP,
        icon_size=52,
        icon_color=ft.colors.WHITE,
        tooltip='Распознать',
        on_click=lambda _: pg.navigator.navigate('/statistics_page', page=pg.page, args=(ml_alg(pg.arguments), names))
    )
    
    
    pg.page.appbar = ft.AppBar(
        title=ft.Text(
            value='Введите имена',
            color=ft.colors.WHITE,
            size=52,
            width=700,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_700,
        ),
        center_title=True,
        toolbar_height=80,
        actions=[btn_go_home, btn_go_statistics]
    )

    

    pg.page.add(col)