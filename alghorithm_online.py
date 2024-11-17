import openai
import cv2
import base64
import json


def resize_image(image_path, max_width=800, max_height=600):
    """
    Уменьшает изображение для удобства передачи через API.

    :param image_path: Путь к изображению.
    :param max_width: Максимальная ширина.
    :param max_height: Максимальная высота.
    :return: Закодированное в base64 уменьшенное изображение.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Изображение не найдено по пути: {image_path}")

    h, w = image.shape[:2]
    scale = min(max_width / w, max_height / h)
    if scale < 1.0:
        resized = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        resized = image

    _, buffer = cv2.imencode('.jpg', resized)
    return base64.b64encode(buffer).decode('utf-8')


def create_prompt(image_base64):
    """
    Создаёт запрос для OpenAI API с изображением в формате base64.

    :param image_base64: Изображение, закодированное в base64.
    :return: Промпт в формате текста.
    """
    prompt = (
        "На изображении представлено табло боулинга. "
        "Проанализируй изображение, выдели имена игроков и их результаты, "
        "и верни данные в формате JSON. "
        "Игроки указаны слева, их результаты отображены напротив. "
        "В каждой строке должно быть ровно 10 значений результатов. "
        "Изображение закодировано в base64:\n"
        f"{image_base64}"
    )
    return prompt

