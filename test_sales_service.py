from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.sales import Sales
from dotenv import load_dotenv
import os

load_dotenv()

# 🔌 Строка подключения к БД AlluresDb
# ALLURES_DB_URL = "mssql+pyodbc://localhost,1433/AlluresDb?driver=ODBC+Driver+17+for+SQL+Server&;Trusted_Connection=yes"

MAINDB_URL = os.getenv("MAINDB_URL")

if MAINDB_URL is None:
    raise ValueError("❌ Переменная MAINDB_URL не найдена. Проверь .env файл.")

engine = create_engine(MAINDB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def main():
    db = SessionLocal()
    try:
        print("🧪 Проверка данных о продажах...")
        sales = db.query(Sales).limit(5).all()

        if not sales:
            print("⚠️ Нет данных о продажах.")
        else:
            for s in sales:
                print(f"✅ ID продажи: {s.id} | Продукт: {s.product_id} | Кол-во: {s.quantity} | Дата: {s.sale_date}")
    except Exception as e:
        print("❌ Ошибка при запросе:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()

