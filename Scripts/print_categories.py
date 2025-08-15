# print_categories.py
from sqlalchemy.orm import Session
from common.db.session import SessionLocal
from common.models.categories import Category

def print_all_categories():
    db: Session = SessionLocal()
    try:
        categories = db.query(Category).all()
        print("📦 Список категорий:")
        for cat in categories:
            print(f"🆔 {cat.category_id} — {cat.name}")
    finally:
        db.close()

if __name__ == "__main__":
    print_all_categories()
