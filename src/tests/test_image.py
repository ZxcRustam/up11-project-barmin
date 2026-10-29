import os

files = [
    "resources/picture.png",
    "resources/IMG_22_001.png",  # замените на файл из вашей БД
    ]

for path in files:
    if os.path.exists(path):
        print(f"{path}: файл есть")
    else:
        print(f"{path}: файла нет")
