## файл для получения первичной сетки

import cv2
import numpy as np
from PIL import Image
import math



def printP(rho, theta, line_image):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 3000 * (-b))
    y1 = int(y0 + 3000 * (a))
    x2 = int(x0 - 3000 * (-b))
    y2 = int(y0 - 3000 * (a))
    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

def printD(A, B, line_image):
    '''
    k = (y1 - y2) / (x1 - x2)
    b = y1 - k * x1
    x3 = x1 + 100
    y3 = k * x3 + b
    '''

    # Определяем вектор направления
    direction_vector = np.array(B) - np.array(A)

    # Нормализуем вектор
    length = np.linalg.norm(direction_vector)
    if length > 0:
        unit_vector = direction_vector / length
    else:
        unit_vector = np.array([0, 0])

    # Увеличиваем длину линии (например, на 50 пикселей в каждую сторону)
    extension_length = 1000
    new_A = (A[0] - unit_vector[0] * extension_length, A[1] - unit_vector[1] * extension_length)
    new_B = (B[0] + unit_vector[0] * extension_length, B[1] + unit_vector[1] * extension_length)

    # cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.line(line_image, (int(new_A[0]), int(new_A[1])), (int(new_B[0]), int(new_B[1])), (0, 255, 0), 2)

def cartesian_to_polar(x, y):
    r = math.sqrt(x2 + y2)

    phi = math.atan2(y, x)

    return r, phi

def polar_line(x1, y1, x2, y2):
    if x1 == x2:
        m = 0
    else:
        m = (y2 - y1) / (x2 - x1)

    theta = math.atan(m)

    phi = math.pi / 2 - theta

    rho = x1 * math.cos(phi) + y1 * math.sin(phi)

    return theta, rho

def f(A, B):
    # Извлекаем координаты
    x1, y1 = A
    x2, y2 = B

    # Вычисляем угол theta
    theta = np.arctan2(y2 - y1, x2 - x1)
    return theta 
    

    # Приводим угол к градусам
    # theta_degrees = np.degrees(theta)

    # Вычисляем коэффициенты A, B и C для уравнения прямой
    A_coef = y2 - y1
    B_coef = x1 - x2
    C_coef = x2 * y1 - x1 * y2

    # Вычисляем расстояние rho от начала координат (0, 0)
    rho = abs(A_coef * 0 + B_coef * 0 + C_coef) / np.sqrt(A_coef**2 + B_coef**2)
    # Вычисляем расстояние rho

    return rho, theta
    # Результаты
    print(f"Угол θ (в радианах): {theta}")
    print(f"Угол θ (в градусах): {theta_degrees}")
    print(f"Расстояние ρ: {rho}")

k = 0
for i in range(16):
    # 1. Загрузка изображения
    image = cv2.imread(f'resized3/{i}.JPG')

    # 2. Преобразование в серый цвет
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3. Применение гауссовского размытия для устранения шума
    # --> Вот данный парамет иногда затирает таблицу, поэтому лучше вначале
    # держать его закоменченным <--
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4. Применение бинаризации
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # --> Откоментирую, чтобы посмотреть как выглядит чб изображение <--
    # cv2_imshow(binary)

    # 5. Обнаружение границ
    edges = cv2.Canny(binary, 100, 200)

    # 6. Применение HoughLines для обнаружения линий
    # --> Тут меняем параметр threshold. Обычно он находится в районе от 120 до 150 <--
    # lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=145)
    # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=200, minLineLength=100, maxLineGap=10)
    # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=200, minLineLength=100, maxLineGap=10)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=90, maxLineGap=9)

    # 7. Копирование исходного изображения для отображения линий
    line_image = image.copy()

    # 8. Рисование найденных линий (точнее отрезков)
    lst = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # print(type(x1))
            A = (x1, y1)
            B = (x2, y2)

            theta = np.arctan2(y2 - y1, x2 - x1)  # Угол в радианах
            if (theta < 0):
                print("here")
                theta = 3.1415 + theta
            


            # rho, theta = f(A, B)
#j            theta, rho = polar_line(A[0], A[1], B[0], B[1])

            #if (theta >= 1.6 and theta <= 1.7) or (theta >= 0 and theta <= 0.2) or (theta <= 3.14 and theta >= 3.1):
            #(theta <= -1.5 and theta >= -1.7): # or (theta <= 0 and theta >= -0.2) or (theta >= -3.14 and theta <= -2.9):
                #print(theta)
            lst.append((A, B, theta))

            #if (True):
                #printD(A, B, line_image)

            # printP(rho, theta, line_image)

    lst = sorted(lst, key = lambda x: x[2]) 
    groups = []
    tmp = []
    for g in range(len(lst)):
        if (not len(tmp)):
            # print("here")
            tmp.append(lst[g])
        elif (abs(tmp[-1][2] - lst[g][2]) <= 0.04):
            # print('2')
            tmp.append(lst[g])
        else:
            groups.append(tmp)
            tmp = []
    groups.append(tmp) 
    print("k", k)
    k += 1
    
    groups = sorted(groups,reverse=True, key = lambda x: len(x))
    groups = groups[:2]
    #for i in range(len(groups)):
    #    print(groups[i])
    #    print("--------------------")

    
    for g in range(len(groups)):
        for j in range(len(groups[g])):
            
            A, B, theta = groups[g][j]
            #x1, y1 = A
            #x2, y2 = B
            print(A, B, theta)
            printD(A, B, line_image)
        print("-----")


    # 9. Отображение результата
    # Если не работает, используйте cv2.imshow(...)
     #cv2.imshow('df', line_image)
    cv2.imwrite(f"hLinesP3/{i}.png", line_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
