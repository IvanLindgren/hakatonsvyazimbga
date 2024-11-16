import json

some_dict = {
  "p": [
    9, 28, 47, 56, 65, 83, 91, 100, 120, 140
  ],
  "m": [
    1, 18, 37, 46, 63, 66, 71, 110, 123, 144
  ]
}

def send_photo(file_photo):
    # Сохраняем JSON данные в файл
    file_path = "json_from_ml/data.json"  # Путь к файлу
    with open(file_path, "w") as json_file:
        json.dump(some_dict, json_file, indent=3)
    return file_path  # Возвращаем путь к файлу