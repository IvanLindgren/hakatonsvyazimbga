import flet as ft # Фреймворк для создания графического приложения
from flet_navigator import *
from utils.Buttons import Button


@route('/viewing_photos')
def viewing_photos(pg: PageData) -> None:
    
    # Список путей к выбранным на предыдущей странице файлам
    pathes = pg.arguments
    
    # Следующее фото
    def next_photo(e) -> None:
        cur_index = images.index(cur_photo.content)
        if cur_index < len(images) - 1:
            cur_photo.content = images[cur_index + 1]
        cur_photo.update()
        
    # Предыдущее фото
    def prev_photo(e) -> None:
        cur_index = images.index(cur_photo.content)
        if cur_index >= 1:
            cur_photo.content = images[cur_index - 1]
        cur_photo.update()
        
     # Настройки окна программы
    pg.page.title = 'Просмотр фото'
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

    btn_recognize = Button(val='Ввести имена', page=pg.page, height=52).create_btn()
    btn_recognize.on_click = lambda _: pg.navigator.navigate('/manage_names_page', page=pg.page, args=pathes[images.index(cur_photo.content)])

    # Верхняя панель приложенияы
    pg.page.appbar = ft.AppBar(
        title=ft.Text(
            value='Просмотр фото',
            color=ft.colors.WHITE,
            size=52,
            width=400,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_700,
        ),
        center_title=True,
        toolbar_height=80,
        actions = [btn_go_home]
    )

    # Создадим кнопки - иконки
    btn_next_photo = ft.IconButton(
        icon=ft.icons.ARROW_RIGHT,
        icon_size=40,
        icon_color=ft.colors.WHITE,
        tooltip='Следующее фото',
    )
    
    btn_prev_photo = ft.IconButton(
        icon=ft.icons.ARROW_LEFT,
        icon_size=40,
        icon_color=ft.colors.WHITE,
        tooltip='Предыдущее фото'
    )

    # Зададим кнопкам соотвествующие функции
    btn_next_photo.on_click = next_photo
    btn_prev_photo.on_click = prev_photo
    
    
    images = []
    for path in pathes:
        if isinstance(path, bytes):
            images.append(ft.Image(src_base64=path.decode('utf-8')))
        else:
            images.append(ft.Image(path))

    # Объект, поверх которого будут выводиться текущее фото
    cur_photo = ft.Card(
        content=images[0],
        width=700,
        height=500,
        shape=ft.RoundedRectangleBorder(radius=20)
    )

    # Добавляем все созданные объекты на страницу
    all_content = ft.Column(
        [
            btn_recognize,
            ft.Row([btn_prev_photo, cur_photo, btn_next_photo], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    pg.page.add(all_content)
