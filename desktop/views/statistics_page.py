import flet as ft
from flet_navigator import *
import matplotlib.pyplot as plt
import datetime
import json
from desktop.utils.Buttons import Button


@route('/statistics_page')
def statistics_page(pg: PageData) -> None:
    def calculate_scores(player_results):
        """
        Рассчитывает очки на основе заданных правил.
        :param player_results: Список результатов игрока.
        :return: Сумма очков, среднее значение и динамика.
        """
        total_points = sum(player_results)
        average_points = total_points / len(player_results)
        dynamic_scores = [
            (result - 100) // 30 for result in player_results
        ]
        return total_points, average_points, dynamic_scores

    def generate_table(players_scores, names):
        """
        Генерирует таблицу с результатами игроков.
        """
        table_rows = []
        for player, scores in players_scores.items():
            name = names.get(player, player)
            if name is None:
                name = f"Игрок {player}"

            total = sum(scores) if scores else 0
            average = round(total / len(scores), 2) if scores else 0
            score_list = " → ".join(map(str, scores)) if scores else "Нет данных"

            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(name)),
                        ft.DataCell(ft.Text(str(total))),
                        ft.DataCell(ft.Text(str(average))),
                        ft.DataCell(ft.Text(score_list)),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Имя игрока")),
                ft.DataColumn(ft.Text("Сумма очков")),
                ft.DataColumn(ft.Text("Среднее")),
                ft.DataColumn(ft.Text("Результаты")),
            ],
            rows=table_rows
        )

        output.content = table
        pg.page.update()

    def plot_player_performance(players_scores):
        """
        Строит график результативности игроков.
        :param players_scores: Словарь с результатами игроков.
        """
        for player, scores in players_scores.items():
            plt.plot(range(1, len(scores) + 1), scores, marker="o", label=player)

        plt.title("Результативность игроков")
        plt.xlabel("Игра")
        plt.ylabel("Очки")
        plt.legend()
        plt.grid(True)
        plt.show()

    def btn_generate_table_click(e):
        generate_table(players_scores, names)

    def btn_plot_player_performance_click(e):
        plot_player_performance(players_scores)

    players_scores, names = pg.arguments
    players_scores = json.loads(players_scores)

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

    btn_generate_table = Button(val='Показать результаты', page=pg.page).create_btn()
    btn_generate_table.on_click = btn_generate_table_click
    btn_plot_player_performance = Button(val='Графики', page=pg.page).create_btn()
    btn_plot_player_performance.on_click = btn_plot_player_performance_click

    output = ft.Card(
        height=500,
        width=800,
    )

    btns = ft.Row(
        controls=[
            btn_generate_table,
            btn_plot_player_performance
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    pg.page.add(ft.Column([btns, output], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
