import cv2
import numpy as np
import easyocr
import json
import os
from sklearn.linear_model import LinearRegression
from pathlib import Path

def ml_alghorithm(path: str):

    def show_image(title, image, is_color=True):
        """
        Вспомогательная функция для отображения изображения.
        """
        if is_color:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def resize_image(image, max_width=800, max_height=600):
        """
        Уменьшает изображение для удобства отображения и обработки.

        :param image: Входное изображение (numpy.ndarray).
        :param max_width: Максимальная ширина.
        :param max_height: Максимальная высота.
        :return: Кортеж из уменьшенного изображения и коэффициента масштаба.
        """
        h, w = image.shape[:2]
        scale = min(max_width / w, max_height / h)
        if scale < 1.0:
            resized = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            return resized, scale
        return image, 1.0


    def warp_perspective(image, points):
        """
        Преобразует изображение, используя указанные точки, чтобы исправить перспективу.
        """
        width = int(max(
            np.linalg.norm(points[1] - points[0]),
            np.linalg.norm(points[3] - points[2])
        ))
        height = int(max(
            np.linalg.norm(points[3] - points[0]),
            np.linalg.norm(points[2] - points[1])
        ))

        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype="float32")

        matrix = cv2.getPerspectiveTransform(points, dst)
        warped_image = cv2.warpPerspective(image, matrix, (width, height))
        return warped_image


    def select_points(image, num_points, max_width=800, max_height=600):
        """
        Позволяет пользователю выбрать точки на уменьшенном изображении.

        :param image: Входное изображение (numpy.ndarray).
        :param num_points: Количество точек для выбора.
        :param max_width: Максимальная ширина.
        :param max_height: Максимальная высота.
        :return: Массив выбранных точек (numpy.ndarray).
        """
        resized_image, scale = resize_image(image, max_width, max_height)
        points = []

        def click_event(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Выбор точек", temp_image)
                if len(points) == num_points:
                    cv2.destroyAllWindows()

        temp_image = resized_image.copy()
        cv2.imshow("Выбор точек", temp_image)
        cv2.setMouseCallback("Выбор точек", click_event)
        print(f"Пожалуйста, выберите {num_points} точку(и) на изображении.")
        cv2.waitKey(0)

        if len(points) != num_points:
            raise ValueError(f"Необходимо выбрать ровно {num_points} точек.")
        return np.array(points, dtype="float32") / scale


    def get_grid_lines(image, file_path="grid_lines.json"):
        """
        Пользователь выбирает линии сетки (горизонтальные и вертикальные) для разделения на 40 ячеек.
        """
        while True:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    grid_lines = json.load(f)
                return grid_lines

            print("Выберите точки для горизонтальных линий.")
            horizontal_points = select_points(image, 11)

            print("Выберите точки для вертикальных линий.")
            vertical_points = select_points(image, 5)

            horizontal_lines = sorted([int(point[1]) for point in horizontal_points])
            vertical_lines = sorted([int(point[0]) for point in vertical_points])

            grid_lines = {
                "horizontal": horizontal_lines,
                "vertical": vertical_lines
            }

            with open(file_path, "w") as f:
                json.dump(grid_lines, f)
            return grid_lines


    def split_into_custom_grid(image, grid_lines):
        """
        Делит изображение на 40 ячеек, используя линии из grid_lines.
        """
        horizontal_lines = grid_lines["horizontal"]
        vertical_lines = grid_lines["vertical"]

        grid_cells = []
        for i in range(len(horizontal_lines) - 1):
            for j in range(len(vertical_lines) - 1):
                cell = image[horizontal_lines[i]:horizontal_lines[i + 1],
                    vertical_lines[j]:vertical_lines[j + 1]]
                grid_cells.append(cell)

        return grid_cells[:40]  # Всегда возвращаем 40 ячеек


    def enhance_cell(cell):
        """
        Переводит ячейку в чёрно-белое изображение.
        """
        if len(cell.shape) == 3:
            cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        return cell


    def recognize_cells_with_ocr(cells):
        """
        Распознаёт текст в каждой ячейке с помощью EasyOCR.
        """
        reader = easyocr.Reader(['en'], gpu=False)
        results = []
        for cell in cells:
            enhanced_cell = enhance_cell(cell)
            ocr_results = reader.readtext(enhanced_cell)
            if ocr_results:
                text = " ".join([res[1] for res in ocr_results]).strip()
                results.append(text)
            else:
                results.append("")
        return results


    def parse_bowling_scores(scores):
        """
        Интерпретирует данные с табло в виде счёта игроков.
        """
        players_scores = {"p1": [], "p2": [], "p3": [], "p4": []}
        current_player = 0

        for score in scores:
            try:
                score = int(score.split()[-1])  # Берём последний элемент в строке
                if players_scores[f"p{current_player + 1}"] and score < players_scores[f"p{current_player + 1}"][-1]:
                    current_player += 1
                if current_player < 4:
                    players_scores[f"p{current_player + 1}"].append(score)
            except (ValueError, IndexError):
                continue

        for player in players_scores:
            if len(players_scores[player]) < 10:
                scores = np.arange(10).reshape(-1, 1)
                model = LinearRegression()
                model.fit(scores[:len(players_scores[player])], players_scores[player])
                predicted_scores = model.predict(scores[len(players_scores[player]):])
                players_scores[player] += list(map(int, predicted_scores))
            players_scores[player] = players_scores[player][:10]
        return players_scores


    def process_bowling_scoreboard(image_path):
        """
        Основной процесс обработки табло.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Изображение не найдено.")

        points = select_points(image, 4)
        roi = warp_perspective(image, points)

        grid_lines = get_grid_lines(roi)
        cells = split_into_custom_grid(roi, grid_lines)
        ocr_results = recognize_cells_with_ocr(cells)

        return parse_bowling_scores(ocr_results)


    
    image_path = path
    if not os.path.exists(image_path):
        print('Изображение не найдено')
    else:
        players_scores = process_bowling_scoreboard(image_path)
        print(json.dumps(players_scores, indent=4, ensure_ascii=False))

ml_alghorithm('C:\\Users\\user\\Desktop\\test\\archive\\2021-09-02 18-27-27.JPG')

