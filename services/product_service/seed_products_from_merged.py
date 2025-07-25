import pandas as pd
import random
from datetime import datetime
from sqlalchemy.orm import Session
from common.db.session import SessionLocal
from common.models.products import Product

# Сопоставление masterCategory → category_id из твоей БД
category_map = {
    "electronics": 1, "bags": 2, "fashion": 3, "personal_care": 4, "toys": 5,
    "home": 6, "food": 7, "outdoor": 8, "military": 9, "automotive": 10,
    "medical": 11, "office": 12, "sports": 13, "art": 14, "pets": 15,
    "diy": 16, "books": 17, "beauty": 18, "gadgets": 19
}

def seed_products():
    db: Session = SessionLocal()
    df = pd.read_csv("merged_fashion_dataset.csv", encoding="utf-8-sig")
    products = []

    for _, row in df.iterrows():
        category_name = str(row.get("masterCategory", "")).lower()
        category_id = category_map.get(category_name)
        if not category_id:
            print(f"[❗] Пропущена категория: {category_name}")
            continue

        name = str(row.get("productDisplayName", "No Name")).capitalize()
        description = f"{name} in category {category_name}"
        price = round(random.uniform(300, 2000), 2)
        old_price = price + round(random.uniform(10, 200), 2)
        image = f"/static/products/{row.get('image', '')}"

        product = Product(
            name=name,
            description=description,
            price=price,
            old_price=old_price,
            image=image,
            status="active",
            current_inventory=random.randint(10, 100),
            is_hit=random.choice([True, False]),
            is_discount=random.choice([True, False]),
            is_new=random.choice([True, False]),
            category_id=category_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        products.append(product)

    db.bulk_save_objects(products)
    db.commit()
    db.close()
    print(f"✅ Загружено {len(products)} товаров в Supabase (таблица products)")

if __name__ == "__main__":
    seed_products()

