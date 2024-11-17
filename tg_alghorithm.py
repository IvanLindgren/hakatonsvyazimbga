import cv2
import numpy as np
import easyocr
import json
from sklearn.linear_model import LinearRegression


def resize_to_fixed_resolution(image, width=1024, height=768):
    """
    Приводит изображение к фиксированному разрешению.
    :param image: Исходное изображение.
    :param width: Ширина изображения.
    :param height: Высота изображения.
    :return: Изображение фиксированного размера.
    """
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def reflect_and_rotate(image):
    """
    Отражает изображение по горизонтали и поворачивает против часовой стрелки.
    :param image: Исходное изображение.
    :return: Преобразованное изображение.
    """
    flipped = cv2.flip(image, 1)  # Отражение по горизонтали
    rotated = cv2.rotate(flipped, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Поворот против часовой стрелки
    return rotated


def warp_perspective(image, points):
    """
    Преобразует изображение с заданными координатами и исправляет перспективу.
    :param image: Исходное изображение.
    :param points: Координаты углов табло.
    :return: Преобразованное изображение.
    """
    width, height = 1024, 768
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    matrix = cv2.getPerspectiveTransform(points, dst)
    return cv2.warpPerspective(image, matrix, (width, height))


def crop_board(image):
    """
    Обрезает область табло по заданным координатам.
    :param image: Исходное изображение.
    :return: Обрезанное изображение.
    """
    x1, y1 = 173, 216
    x2, y2 = 669, 695
    return image[y1:y2, x1:x2]


def split_into_grid(image):
    """
    Делит изображение на ячейки с использованием фиксированных линий сетки.
    :param image: Преобразованное изображение табло.
    :return: Список ячеек.
    """
    grid_lines = {
        "horizontal": [0, 120, 240, 360, 480],  # Линии для строк
        "vertical": [0, 100, 200, 300, 400, 500]  # Линии для столбцов
    }
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
    :param cell: Исходная ячейка.
    :return: Обработанная ячейка.
    """
    if len(cell.shape) == 3:
        cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    return cell


def recognize_cells_with_ocr(cells):
    """
    Распознаёт текст в каждой ячейке с помощью EasyOCR.
    :param cells: Список ячеек для обработки.
    :return: Список распознанных текстов.
    """
    reader = easyocr.Reader(['en'], gpu=False)
    results = []
    for cell in cells:
        enhanced_cell = enhance_cell(cell)
        enlarged_cell = cv2.resize(enhanced_cell, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        ocr_results = reader.readtext(enlarged_cell)

        if ocr_results:
            text = " ".join([res[1] for res in ocr_results]).strip()
            results.append(text)
        else:
            results.append("")
    return results


def parse_bowling_scores(scores):
    """
    Интерпретирует результаты боулинга.
    :param scores: Распознанные данные из ячеек.
    :return: Структурированные результаты.
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
        existing_scores = players_scores[player]
        if len(existing_scores) < 10:
            if existing_scores:
                # Заполнение пропущенных значений с помощью линейной регрессии
                x = np.arange(len(existing_scores)).reshape(-1, 1)
                y = np.array(existing_scores)
                model = LinearRegression()
                model.fit(x, y)
                missing_x = np.arange(len(existing_scores), 10).reshape(-1, 1)
                predicted_scores = model.predict(missing_x)
                predicted_scores = [int(pred) for pred in predicted_scores if pred <= 250]
                players_scores[player] += predicted_scores
            else:
                # Если нет данных, заполняем нулями
                players_scores[player] += [0] * (10 - len(existing_scores))

        players_scores[player] = players_scores[player][:10]

    return players_scores


def process_image(image_path):
    """
    Основная функция обработки изображения.
    :param image_path: Путь к изображению.
    :return: JSON с результатами.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Изображение не найдено.")

    # Отражение и поворот изображения
    image = reflect_and_rotate(image)

    # Преобразование перспективы
    points = np.array([
        [173, 216],
        [669, 216],
        [669, 695],
        [176, 695]
    ], dtype="float32")
    warped = warp_perspective(image, points)

    # Обрезаем изображение по координатам табло
    cropped = crop_board(warped)

    # Разделение на ячейки
    cells = split_into_grid(cropped)

    # Распознавание текста в ячейках
    ocr_results = recognize_cells_with_ocr(cells)

    # Парсинг результатов
    return parse_bowling_scores(ocr_results)


if __name__ == "__main__":
    image_path = "photos/2021-09-02/2021-09-02 18-27-27.JPG"
    results = process_image(image_path)
    print(json.dumps(results, indent=4, ensure_ascii=False))
