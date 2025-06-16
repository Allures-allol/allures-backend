# common/db/product_connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.review_service.common.config.settings_review import settings_review  # путь до настроек

engine = create_engine(settings_review.MAINDB_URL, echo=True)
ProductSessionLocal = sessionmaker(bind=engine)

def get_product_db():
    db = ProductSessionLocal()
    try:
        yield db
    finally:
        db.close()
