# common/db/product_connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ALLURES_DB_URL = os.getenv("ALLURES_DB_URL")

engine = create_engine(ALLURES_DB_URL)
ProductSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

