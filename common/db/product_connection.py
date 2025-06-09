# common/db/product_connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

MAINDB_URL = os.getenv("MAINDB_URL")
if MAINDB_URL is None:
    raise ValueError("❌ MAINDB_URL не найден")

engine = create_engine(MAINDB_URL, echo=True)
ProductSessionLocal = sessionmaker(bind=engine)
