import cv2
import numpy as np
from main import show_image

# 1. Загрузка изображения
image = cv2.imread("photos/2024-10-01/2024-10-01 19-01-57.JPG")

# 2. Преобразование в серый цвет
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 3. Применение гауссовского размытия для устранения шума
# --> Вот данный парамет иногда затирает таблицу, поэтому лучше вначале
# держать его закоменченным <--
# gray = cv2.GaussianBlur(gray, (5, 5), 0)

# 4. Применение бинаризации
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# --> Откоментирую, чтобы посмотреть как выглядит чб изображение <--
# cv2_imshow(binary)

# 5. Обнаружение границ
edges = cv2.Canny(binary, 50, 150)

# 6. Применение HoughLines для обнаружения линий
# --> Тут меняем параметр threshold. Обычно он находится в районе от 120 до 150 <--
lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=145)

# 7. Копирование исходного изображения для отображения линий
line_image = image.copy()

# 8. Рисование найденных линий (точнее отрезков)
if lines is not None:
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1500 * (-b))
        y1 = int(y0 + 1500 * (a))
        x2 = int(x0 - 1500 * (-b))
        y2 = int(y0 - 1500 * (a))
        cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

# 9. Отображение результата
# Если не работает, используйте cv2.imshow(...)
show_image("test", line_image)
