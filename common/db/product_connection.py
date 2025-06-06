# common/db/product_connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ALLURES_DB_URL = "mssql+pyodbc://sa:L#8rMw2$Dn!eX4qJ@switchyard.proxy.rlwy.net:54488/<имя_базы>?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(ALLURES_DB_URL)
ProductSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

