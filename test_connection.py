# test_connection.py
from dotenv import load_dotenv
from common.db.product_connection import ProductSessionLocal

load_dotenv()

def test_db_connection():
    db = None
    try:
        db = ProductSessionLocal()
        db.execute("SELECT 1")
        print("✅ Успешное подключение к базе данных!")
    except Exception as e:
        print("❌ Ошибка подключения:", e)
        assert False, f"Ошибка подключения: {e}"
    finally:
        if db:
            db.close()
