import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('1.jpeg')

# Преобразование в серый цвет
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Применение гауссовского размытия для устранения шума
# Применяем, только если без этого никак
# gray = cv2.GaussianBlur(gray, (5, 5), 0)

# Применение бинаризации
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)


# Обнаружение границ
# edges = cv2.Canny(binary, 50, 150, apertureSize=3)
edges = cv2.Canny(binary, 50, 150)


# --> Тут меняем параметры threshold, minLenght и Gap <--
# Применение преобразования Хафа
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=145, minLineLength=150, maxLineGap=10)
#lines = cv2.HoughLinesP(edges, 1, 1*np.pi/180, threshold=40 , minLineLength=40, 40, 6 )

# Копирование исходного изображения для отображения сетки
grid_image = image.copy()

# Рисование найденных горизонтальных и вертикальных линий
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(grid_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Отображение результата
cv2_imshow(grid_image)
cv2.waitKey(0)
cv2.destroyAllWindows()