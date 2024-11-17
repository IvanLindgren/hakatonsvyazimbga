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
        return f"Всего очков {total_points}, Среднее значение {average_points}, Динамика {dynamic_scores}"
        return total_points, average_points, dynamic_scores


    def generate_daily_report(players_scores):
        """
        Генерирует отчет по игрокам на основе данных за день.
        :param players_scores: Результаты игроков.
        :return: Отчет в виде словаря.
        """
        report = {}
        for player, scores in players_scores.items():
            total, average, dynamics = calculate_scores(scores)
            report[player] = {
                "Игры": len(scores),
                "Сумма очков": total,
                "Средний результат": round(average, 2),
                "Динамика": dynamics,
                "Результаты по играм": scores
            }
        return report


    def generate_period_report(players_scores_by_day):
        """
        Генерирует отчет за несколько дней.
        :param players_scores_by_day: Словарь с данными за каждый день.
        :return: Отчет в виде словаря.
        """
        report = {}
        for date, daily_scores in players_scores_by_day.items():
            daily_report = generate_daily_report(daily_scores)
            report[date] = daily_report
        return report


    def log_process(message):
        """
        Выводит сообщения в лог программы.
        :param message: Текст сообщения.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")


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
    
    def btn_calculate_scores_click(e):
        output.content = ft.Column(
            [
                ft.Text(value=f" Игрок {names['p1']}: {calculate_scores(players_scores['p1'])}", color=ft.colors.WHITE),
                ft.Text(value=f" Игрок {names['p2']}: {calculate_scores(players_scores['p2'])}", color=ft.colors.WHITE),
                ft.Text(value=f" Игрок {names['p3']}: {calculate_scores(players_scores['p3'])}", color=ft.colors.WHITE),
                ft.Text(value=f" Игрок {names['p4']}: {calculate_scores(players_scores['p4'])}", color=ft.colors.WHITE)
            ],
            horizontal_alignment=ft.MainAxisAlignment.CENTER
        )
        pg.page.update()

    def btn_generate_daily_report_click(e):
        pass

    
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

    btn_calculate_scores = Button(val='Статистика', page=pg.page).create_btn()
    btn_calculate_scores.on_click = btn_calculate_scores_click
    #btn_generate_daily_report = Button(val='Отчет за день', page=pg.page).create_btn()
    btn_plot_player_performance = Button(val='Графики', page=pg.page).create_btn()
    btn_plot_player_performance.on_click = lambda _: plot_player_performance(players_scores)


    output = ft.Card(
        height=500, 
        width=800,
    )

    btns = ft.Row(
        controls=[
            btn_calculate_scores,
            btn_plot_player_performance
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    pg.page.add(ft.Column([btns, output], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
    

    


    