# 📁 common/models/uploads.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from common.db.base import Base

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("admin.id"))
    image_url = Column(String)
    result_text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="uploads")

