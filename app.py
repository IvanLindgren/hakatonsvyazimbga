import flet as ft
from flet_navigator import *
from views.home_page import home_page
from views.viewing_photos import viewing_photos


def main(page: ft.Page) -> None:
    
    navigator = VirtualFletNavigator(
        routes={
            '/': home_page,
            '/viewing_photos': viewing_photos
        },
        navigator_animation=NavigatorAnimation(NavigatorAnimation.FADE)
    )

    navigator.render(page)


if __name__ == '__main__':
    ft.app(target=main)