import cv2
import numpy as np
import easyocr


def preprocess_image(image_path):
    """Предобработка изображения для OCR без обрезки, адаптированная для табло."""
    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка загрузки изображения. Проверьте путь к файлу.")
        return None

    # Преобразование в оттенки серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Увеличение контрастности с использованием CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Легкое размытие для сглаживания изображения
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Мягкая бинаризация
    _, binary = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY_INV)

    # Применение морфологической операции закрытия, чтобы укрепить линии текста
    kernel = np.ones((2, 2), np.uint8)
    processed_image = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return processed_image


def extract_text_from_image(image):
    """Извлечение текста из изображения с использованием EasyOCR без обрезки."""
    reader = easyocr.Reader(['en'], gpu=False)  # Используем английский для точности
    # Распознаем текст на всем изображении
    results = reader.readtext(image, detail=0, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/X")
    return results


def main(image_path):
    # Предобработка изображения
    processed_image = preprocess_image(image_path)

    # Извлечение текста из полного изображения
    text = extract_text_from_image(processed_image)

    # Печать результатов
    print("Распознанный текст:")
    for line in text:
        print(line)


# Пример использования
image_path = "photos/2024-10-01/2024-10-01 19-01-57.JPG"  # Укажите путь к изображению
main(image_path)
