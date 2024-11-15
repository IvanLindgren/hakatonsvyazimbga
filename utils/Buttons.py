import flet as ft


# Класс, который отвечает за создание типовых кнопок, которые используются во всем приложении
class Button:
    # Инициализация входных параметров
    def __init__(self, page: ft.Page, width=400, height=80, val=None, icon_name=ft.icons.HOME) -> None:
        self.val = val
        self.width = width
        self.page = page
        self.icon_name = icon_name
        self.height = height
    
    # Создание кнопки на основе входных параметров
    def create_btn(self) -> ft.ElevatedButton:
        
        txt = ft.Text(value=self.val,
                      color=ft.colors.WHITE,
                      text_align=ft.TextAlign.CENTER,
                      size=30,
                      weight=ft.FontWeight.W_700,
        )
        
        btn = ft.ElevatedButton(style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                width=self.width,
                                height=self.height,
                                content=ft.Row(
                                    [
                                        ft.Icon(self.icon_name, size=30, color=ft.colors.WHITE),
                                        txt
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=30
                                )
        )
        
        return btn
