import cv2
import numpy as np
import easyocr
import json
import os
from sklearn.linear_model import LinearRegression


def resize_to_fixed_resolution(image, width=1024, height=768):
    """
    Приводит изображение к фиксированному разрешению.
    """
    resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return resized_image


def warp_perspective(image, points):
    """
    Преобразует изображение, исправляя перспективу, и приводит к фиксированному разрешению.
    """
    width, height = 1024, 768
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    matrix = cv2.getPerspectiveTransform(points, dst)
    warped_image = cv2.warpPerspective(image, matrix, (width, height))
    return warped_image


def select_points(image, num_points):
    """
    Позволяет пользователю выбрать точки на изображении.
    """
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Выбор точек", temp_image)
            if len(points) == num_points:
                cv2.destroyAllWindows()

    temp_image = image.copy()
    cv2.imshow("Выбор точек", temp_image)
    cv2.setMouseCallback("Выбор точек", click_event)
    print(f"Пожалуйста, выберите {num_points} точки на изображении.")
    cv2.waitKey(0)

    if len(points) != num_points:
        raise ValueError(f"Необходимо выбрать ровно {num_points} точки.")
    return np.array(points, dtype="float32")


def get_grid_lines(image, file_path="grid_lines.json"):
    """
    Пользователь выбирает линии сетки (горизонтальные и вертикальные).
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            grid_lines = json.load(f)
        return grid_lines

    print("Выберите горизонтальные линии (5 линий).")
    horizontal_points = select_points(image, 5)
    print("Выберите вертикальные линии (11 линий).")
    vertical_points = select_points(image, 11)

    horizontal_lines = sorted([int(point[1]) for point in horizontal_points])
    vertical_lines = sorted([int(point[0]) for point in vertical_points])

    grid_lines = {"horizontal": horizontal_lines, "vertical": vertical_lines}
    with open(file_path, "w") as f:
        json.dump(grid_lines, f)
    return grid_lines


def split_into_grid(image, grid_lines):
    """
    Делит изображение на ячейки с использованием линий сетки.
    """
    horizontal_lines = grid_lines["horizontal"]
    vertical_lines = grid_lines["vertical"]

    grid_cells = []
    for i in range(len(horizontal_lines) - 1):
        for j in range(len(vertical_lines) - 1):
            cell = image[horizontal_lines[i]:horizontal_lines[i + 1],
                         vertical_lines[j]:vertical_lines[j + 1]]
            grid_cells.append(cell)
    return grid_cells[:40]


def enhance_cell(cell):
    """
    Переводит ячейку в черно-белое изображение.
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
    Добавляет фильтрацию некорректных данных:
    1. Исключает значения больше 250.
    2. Проверяет, чтобы результаты всегда увеличивались.
    """
    players_scores = {"p1": [], "p2": [], "p3": [], "p4": []}
    current_player = 0

    for score in scores:
        try:
            # Преобразуем результат в число (берём последний элемент в строке)
            score = int(score.split()[-1])

            # Удаляем значения больше 250
            if score > 250:
                continue

            # Проверяем последовательность значений (должны возрастать)
            if players_scores[f"p{current_player + 1}"]:
                last_score = players_scores[f"p{current_player + 1}"][-1]
                if score < last_score:
                    current_player += 1  # Переход к следующему игроку
                    if current_player >= 4:
                        break  # Если больше 4 игроков, выходим

            # Добавляем результат к текущему игроку
            if current_player < 4:
                players_scores[f"p{current_player + 1}"].append(score)
        except (ValueError, IndexError):
            # Игнорируем ошибки преобразования
            continue

    # Проверяем, есть ли у всех игроков 10 результатов, и дополняем их с помощью линейной регрессии
    for player in players_scores:
        if len(players_scores[player]) < 10:
            existing_scores = players_scores[player]
            if len(existing_scores) > 1:
                # Применяем линейную регрессию для заполнения пропусков
                x = np.arange(len(existing_scores)).reshape(-1, 1)
                y = np.array(existing_scores)
                model = LinearRegression()
                model.fit(x, y)
                missing_x = np.arange(len(existing_scores), 10).reshape(-1, 1)
                predicted_scores = model.predict(missing_x)

                # Исключаем некорректные предсказанные значения (>250)
                predicted_scores = [int(pred) for pred in predicted_scores if pred <= 250]
                players_scores[player] += predicted_scores

            else:
                # Если есть только один результат, дублируем его
                players_scores[player] += [existing_scores[0]] * (10 - len(existing_scores))

        # Убедимся, что у каждого игрока ровно 10 результатов
        players_scores[player] = players_scores[player][:10]

    return players_scores



def process_bowling_scoreboard(image_path):
    """
    Основной процесс обработки табло.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Изображение не найдено.")

    resized_image = resize_to_fixed_resolution(image)
    print("Выберите 4 точки для перспективного преобразования.")
    points = select_points(resized_image, 4)
    roi = warp_perspective(resized_image, points)

    grid_lines = get_grid_lines(roi)
    cells = split_into_grid(roi, grid_lines)
    ocr_results = recognize_cells_with_ocr(cells)

    return parse_bowling_scores(ocr_results)


if __name__ == "__main__":
    image_path = "photos/2021-09-02/2021-09-02 18-27-27.JPG"
    if not os.path.exists(image_path):
        print("Изображение не найдено.")
    else:
        players_scores = process_bowling_scoreboard(image_path)
        print(json.dumps(players_scores, indent=4, ensure_ascii=False))
