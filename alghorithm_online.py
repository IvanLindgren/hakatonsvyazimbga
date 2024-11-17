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


def send_request_to_openai(prompt, api_key):
    """
    Отправляет запрос к OpenAI API.

    :param prompt: Текстовый запрос.
    :param api_key: API-ключ OpenAI.
    :return: Ответ в формате JSON.
    """
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — эксперт по распознаванию изображений."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Ошибка при отправке запроса: {e}")
        return {}


def main():
    """
    Основная функция запуска алгоритма.
    """
    image_path = "photos/2024-10-01/2024-10-01 19-01-57.JPG"
    api_key = "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"  # Вставьте сюда ваш ключ OpenAI

    try:
        # Уменьшение размера изображения и кодирование в base64
        image_base64 = resize_image(image_path)

        # Создание промпта для OpenAI
        prompt = create_prompt(image_base64)

        # Отправка запроса
        response = send_request_to_openai(prompt, api_key)

        # Обработка ответа
        try:
            data = json.loads(response)
            print(json.dumps(data, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print("Не удалось декодировать JSON из ответа OpenAI.")
            print("Ответ от OpenAI:", response)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
