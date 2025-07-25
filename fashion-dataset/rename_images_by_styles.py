import os
import pandas as pd
from collections import defaultdict

# Пути к CSV и папке с изображениями
CSV_PATH = "styles.csv"
IMAGES_DIR = "images"

# Загрузка таблицы
df = pd.read_csv(CSV_PATH, usecols=["id", "articleType"])
df.dropna(inplace=True)

# Словарь: id -> articleType
id_to_name = dict(zip(df["id"].astype(str), df["articleType"].str.lower().str.replace(r"\s+", "_", regex=True)))

# Учёт повторов
name_counter = defaultdict(int)

# Переименование файлов
renamed = 0
for filename in os.listdir(IMAGES_DIR):
    file_id, ext = os.path.splitext(filename)
    if file_id in id_to_name:
        new_name = id_to_name[file_id]
        name_counter[new_name] += 1
        suffix = f"_{name_counter[new_name]}" if name_counter[new_name] > 1 else ""
        new_filename = f"{new_name}{suffix}{ext}"

        old_path = os.path.join(IMAGES_DIR, filename)
        new_path = os.path.join(IMAGES_DIR, new_filename)

        os.rename(old_path, new_path)
        print(f"✅ {filename} → {new_filename}")
        renamed += 1

print(f"\n🎉 Всего переименовано: {renamed} файлов.")
