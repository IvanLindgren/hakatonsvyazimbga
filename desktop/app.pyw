import flet as ft
import warnings
from flet_navigator import *
from views.home_page import home_page
from views.viewing_photos import viewing_photos
from views.statistics_page import statistics_page
from views.manage_names_page import manage_names_page
warnings.filterwarnings('ignore')


def main(page: ft.Page) -> None:
    
    navigator = VirtualFletNavigator(
        routes={
            '/': home_page,
            '/viewing_photos': viewing_photos,
            '/statistics_page': statistics_page,
            '/manage_names_page': manage_names_page
        },
        navigator_animation=NavigatorAnimation(NavigatorAnimation.FADE)
    )

    navigator.render(page)


if __name__ == '__main__':
    ft.app(target=main)