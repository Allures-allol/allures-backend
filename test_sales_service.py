from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.sales import Sales

# 🔌 Строка подключения к БД AlluresDb
ALLURES_DB_URL = "mssql+pyodbc://localhost,1433/AlluresDb?driver=ODBC+Driver+17+for+SQL+Server&;Trusted_Connection=yes"

# ⚙️ Инициализация SQLAlchemy
engine = create_engine(ALLURES_DB_URL)
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
    finally:
        db.close()

if __name__ == "__main__":
    main()
