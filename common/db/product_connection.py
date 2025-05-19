# common/db/product_connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ALLURES_DB_URL = "mssql+pyodbc://localhost,1433/AlluresDb?driver=ODBC%20Driver%2017%20for%20SQL%20Server&;Trusted_Connection=yes"

engine = create_engine(ALLURES_DB_URL)
ProductSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

