import cv2
import numpy as np
import easyocr
import json
import os
from sklearn.linear_model import LinearRegression


def resize_to_fixed_resolution(image, width=1024, height=768):
    """
    Изменяет размер изображения до фиксированного разрешения.
    """
    resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return resized_image


def warp_perspective(image, points):
    """
    Преобразует изображение, исправляя перспективу, и приводит его к фиксированному разрешению.
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
    Позволяет пользователю выбрать точки на изображении для перспективного преобразования.
    """
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Select Points", temp_image)
            if len(points) == num_points:
                cv2.destroyAllWindows()

    temp_image = image.copy()
    cv2.imshow("Select Points", temp_image)
    cv2.setMouseCallback("Select Points", click_event)
    print(f"Пожалуйста, выберите {num_points} точек на изображении.")
    cv2.waitKey(0)

    if len(points) != num_points:
        raise ValueError(f"Необходимо выбрать ровно {num_points} точки.")
    return np.array(points, dtype="float32")


def get_grid_lines(image, file_path="grid_lines.json"):
    """
    Позволяет пользователю определить линии сетки (горизонтальные и вертикальные).
    Если файл с линиями уже существует, использует его.
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
    return grid_cells[:40]  # Возвращаем ровно 40 ячеек


def enhance_cell(cell):
    """
    Преобразует ячейку в изображение оттенков серого.
    """
    if len(cell.shape) == 3:
        cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    return cell


def recognize_cells_with_ocr(cells, show_cells=False):
    """
    Распознаёт текст в каждой ячейке с помощью EasyOCR.
    :param cells: Список ячеек для обработки.
    :param show_cells: Флаг для отображения увеличенных ячеек и распознанного текста.
    """
    reader = easyocr.Reader(['en'], gpu=False)
    results = []
    for idx, cell in enumerate(cells):
        enhanced_cell = enhance_cell(cell)

        # Увеличение ячейки для улучшения распознавания
        enlarged_cell = cv2.resize(enhanced_cell, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        ocr_results = reader.readtext(enlarged_cell)

        if ocr_results:
            text = " ".join([res[1] for res in ocr_results]).strip()
            results.append(text)
        else:
            text = ""
            results.append(text)

        if show_cells:
            print(f"Ячейка {idx + 1}: {text}")
            cv2.imshow(f"Ячейка {idx + 1}", enlarged_cell)
            cv2.waitKey(0)

    if show_cells:
        cv2.destroyAllWindows()

    return results


def parse_bowling_scores(scores):
    """
    Интерпретирует результаты боулинга.
    Удаляет некорректные данные:
    1. Исключает значения >250.
    2. Проверяет, чтобы результаты всегда увеличивались.
    """
    players_scores = {"p1": [], "p2": [], "p3": [], "p4": []}
    current_player = 0

    for score in scores:
        try:
            score = int(score.split()[-1])

            if score > 250:
                continue

            if players_scores[f"p{current_player + 1}"]:
                last_score = players_scores[f"p{current_player + 1}"][-1]
                if score < last_score:
                    current_player += 1
                    if current_player >= 4:
                        break

            if current_player < 4:
                players_scores[f"p{current_player + 1}"].append(score)
        except (ValueError, IndexError):
            continue

    for player in players_scores:
        if len(players_scores[player]) < 10:
            existing_scores = players_scores[player]
            if len(existing_scores) > 1:
                x = np.arange(len(existing_scores)).reshape(-1, 1)
                y = np.array(existing_scores)
                model = LinearRegression()
                model.fit(x, y)
                missing_x = np.arange(len(existing_scores), 10).reshape(-1, 1)
                predicted_scores = model.predict(missing_x)
                predicted_scores = [int(pred) for pred in predicted_scores if pred <= 250]
                players_scores[player] += predicted_scores
            else:
                players_scores[player] += [existing_scores[0]] * (10 - len(existing_scores))

        players_scores[player] = players_scores[player][:10]

    return players_scores


def process_bowling_scoreboard(image_path, show_cells=True):
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
    ocr_results = recognize_cells_with_ocr(cells, show_cells)

    return parse_bowling_scores(ocr_results)


if __name__ == "__main__":
    image_path = "photos/2021-09-02/2021-09-02 18-27-27.JPG"
    if not os.path.exists(image_path):
        print("Изображение не найдено.")
    else:
        players_scores = process_bowling_scoreboard(image_path, show_cells=False)
        print(json.dumps(players_scores, indent=4, ensure_ascii=False))
