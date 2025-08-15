import pandas as pd
from sqlalchemy.orm import Session
from common.models.products import Product
from datetime import datetime
import random

CSV_PATH = "unified_products_catalog.csv"

# Маппинг названий категорий из CSV к category_id из вашей таблицы Supabase
CATEGORY_MAP = {
    "Accessories": 2,        # bags
    "Footwear": 3,           # fashion
    "Apparel": 3,            # fashion
    "Personal Care": 4,
    "Toys": 5,
    "Home": 6,
    "Food": 7,
    "Outdoor": 8,
    "Military": 9,
    "Automotive": 10,
    "Medical": 11,
    "Office": 12,
    "Sports": 13,
    "Sporting Goods": 13,    # Альтернативное имя
    "Art": 14,
    "Pets": 15,
    "Diy": 16,
    "Books": 17,
    "Beauty": 18,
    "Gadgets": 19,
    "Free Items": None       # Исключаем
}

def load_and_classify_bulk(db: Session):
    try:
        df = pd.read_csv(CSV_PATH)
        print("📌 Колонки CSV:", df.columns.tolist())

        count = 0
        for _, row in df.iterrows():
            try:
                # Проверка поля description
                if isinstance(row['description'], str) and "Category:" in row['description']:
                    category_name = row['description'].split("Category:")[1].strip()
                else:
                    product_name = row.get('name') or "Unnamed Product"
                    print(f"⚠️ Пропущено: нет категории в description у товара: {product_name}")
                    continue

                category_id = CATEGORY_MAP.get(category_name)
                if not category_id:
                    print(f"❌ Категория '{category_name}' не найдена в словаре — товар '{row.get('name')}' пропущен")
                    continue

                # Обработка цен
                price = float(row['price'])
                old_price = float(row['old_price']) if not pd.isna(row['old_price']) else None

                product = Product(
                    name=row['name'],
                    description=row['description'],
                    price=price,
                    old_price=old_price,
                    image=row['image'],
                    status=row.get('status', 'active'),
                    current_inventory=int(row.get('current_inventory', random.randint(10, 100))),
                    is_hit=bool(row.get('is_hit', random.choice([True, False]))),
                    is_discount=bool(row.get('is_discount', random.choice([True, False]))),
                    is_new=bool(row.get('is_new', random.choice([True, False]))),
                    category_id=category_id,
                    created_at=pd.to_datetime(row.get('created_at', datetime.utcnow())),
                    updated_at=pd.to_datetime(row.get('updated_at', datetime.utcnow()))
                )

                db.add(product)
                count += 1

            except Exception as inner_err:
                print(f"⚠️ Ошибка при обработке строки '{row.get('name') or 'Unnamed'}': {inner_err}")
                continue

        db.commit()
        print(f"✅ Успешно загружено {count} товаров в базу данных.")

    except FileNotFoundError:
        print(f"⛔ Файл '{CSV_PATH}' не найден.")
    except Exception as e:
        print(f"❌ Общая ошибка при загрузке: {e}")

    print("\n🔍 Категории без сопоставления:")
    missing = df[df['description'].notna() & df['description'].str.contains("Category:")].copy()
    missing['parsed_category'] = missing['description'].str.extract(r'Category:\s*(.*)')
    missing_unique = missing['parsed_category'].dropna().unique()

    for cat in missing_unique:
        if cat not in CATEGORY_MAP:
            print(f"🟡 Не найдена категория: '{cat}' — добавь в CATEGORY_MAP")