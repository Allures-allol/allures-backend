import os
import random
from pathlib import Path
from datetime import datetime
import pandas as pd

# Обновлённое имя папки с изображениями
base_dir = Path("mock_static/products_images_")

# Соответствие category_name → category_id (как в твоей БД)
category_map = {
    "electronics": 1, "bags": 2, "fashion": 3, "personal_care": 4, "toys": 5,
    "home": 6, "food": 7, "outdoor": 8, "military": 9, "automotive": 10,
    "medical": 11, "office": 12, "sports": 13, "art": 14, "pets": 15,
    "diy": 16, "books": 17, "beauty": 18, "gadgets": 19
}

rows = []
for category_dir in base_dir.iterdir():
    if category_dir.is_dir():
        category = category_dir.name.lower()
        category_id = category_map.get(category)
        if not category_id:
            print(f"[!] Категория '{category}' не найдена в category_map")
            continue

        for image in category_dir.glob("*.jpg"):
            name = image.stem.replace("_", " ").capitalize()
            description = f"{name} in category {category}"
            price = round(random.uniform(10, 200), 2)
            old_price = price + round(random.uniform(5, 50), 2)
            now = datetime.utcnow().isoformat()

            rows.append([
                name, description, price, old_price, f"{category}/{image.name}", "active",
                random.randint(10, 100), random.choice([True, False]),
                random.choice([True, False]), random.choice([True, False]),
                category_id, now, now
            ])

# Создание CSV-файла
df = pd.DataFrame(rows, columns=[
    "name", "description", "price", "old_price", "image", "status",
    "current_inventory", "is_hit", "is_discount", "is_new",
    "category_id", "created_at", "updated_at"
])

df.to_csv("products_from_folders.csv", index=False)
print(" CSV готов: products_from_folders.csv")
