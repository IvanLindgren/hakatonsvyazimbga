import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_image(title, image, cmap='gray'):
    """Отображение изображения с использованием matplotlib."""
    plt.figure(figsize=(10, 10))
    plt.title(title)
    plt.imshow(image, cmap=cmap)
    plt.axis('off')
    plt.show()

def detect_lines(image, threshold=120, min_line_length=150, max_line_gap=30):
    """
    Обнаружение линий с помощью преобразования Хаффа.
    """
    edges = cv2.Canny(image, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)

    # Отображение линий Хаффа
    hough_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(hough_image, (x1, y1), (x2, y2), (255, 255, 255), 1)
    show_image("Линии Хаффа", hough_image)

    return lines

def calculate_grid_parameters(lines, axis, min_step=30, fixed_angle=3):
    """
    Рассчитывает параметры сетки (шаг и угол) на основе линий Хаффа.
    """
    if lines is None or len(lines) == 0:
        return None, None

    positions = []
    angles = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        if axis == 'x':  # Вертикальные линии
            positions.append(x1)
        elif axis == 'y':  # Горизонтальные линии
            positions.append(y1)

        # Вычисляем угол наклона линии
        angle = np.arctan2((y2 - y1), (x2 - x1)) * 180 / np.pi
        angles.append(angle)

    # Сортируем линии и фильтруем по минимальному шагу
    positions = sorted(positions)
    filtered_positions = [positions[0]] if positions else []

    for pos in positions[1:]:
        if pos - filtered_positions[-1] > min_step:
            filtered_positions.append(pos)

    # Среднее расстояние между линиями
    steps = [filtered_positions[i] - filtered_positions[i - 1] for i in range(1, len(filtered_positions))]
    avg_step = np.mean(steps) if len(steps) > 0 else min_step

    # Устанавливаем угол наклона фиксированным
    avg_angle = fixed_angle

    return avg_step, avg_angle

def draw_grid(image, avg_step_x, avg_step_y, avg_angle, min_step=30):
    """
    Рисует адаптивную сетку на изображении.
    """
    grid_image = image.copy()
    height, width = grid_image.shape[:2]

    # Параметры для наклона сетки
    rad_angle = np.radians(avg_angle)

    # Рисуем вертикальные линии
    x = 0
    while x < width:
        x_offset = int(np.tan(rad_angle) * height)  # Удлинение по вертикали
        cv2.line(grid_image, (int(x), 0), (int(x + x_offset), height), (0, 255, 0), 1)
        x += max(avg_step_x, min_step)

    # Рисуем горизонтальные линии
    y = 0
    while y < height:
        y_offset = int(np.tan(rad_angle) * width)  # Удлинение по горизонтали
        cv2.line(grid_image, (0, int(y)), (width, int(y + y_offset)), (0, 255, 0), 1)
        y += max(avg_step_y, min_step)

    return grid_image

def process_image(image_path):
    """
    Основная функция для обработки изображения и наложения адаптивной сетки.
    """
    # 1. Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка загрузки изображения.")
        return

    # 2. Преобразование в серый цвет
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3. Бинаризация
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    show_image("Бинаризированное изображение", binary)

    # 4. Обнаружение линий Хаффа
    lines = detect_lines(binary, threshold=120, min_line_length=150, max_line_gap=30)

    # 5. Расчет параметров сетки
    avg_step_x, avg_angle_x = calculate_grid_parameters(lines, axis='x', min_step=154, fixed_angle=3)
    avg_step_y, avg_angle_y = calculate_grid_parameters(lines, axis='y', min_step=154, fixed_angle=2)

    print(f"Средний шаг по X: {avg_step_x}, Угол: {avg_angle_x}")
    print(f"Средний шаг по Y: {avg_step_y}, Угол: {avg_angle_y}")

    # 6. Наложение сетки
    grid_image = draw_grid(image, avg_step_x, avg_step_y, avg_angle_x)
    show_image("Изображение с адаптивной сеткой", grid_image)

# Путь к изображению
image_path = "photos/2024-10-01/2024-10-01 19-01-57.JPG"
process_image(image_path)
