# services/common/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Чтение строки подключения из .env.review
# ALLURES_DB_URL= os.getenv("ALLURES_DB_URL", "mssql+pyodbc://sa:StrongPass123!@mssql-db:1433/AlluresDb?driver=ODBC+Driver+17+for+SQL+Server")
ALLURES_DB_URL="mssql+pyodbc://sa:L#8rMw2$Dn!eX4qJ@switchyard.proxy.rlwy.net:54488/<имя_базы>?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(ALLURES_DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

