# 📁 common/models/subscription.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    product_limit = Column(Integer, default=0)
    promo_balance = Column(Integer, default=0)
    support_level = Column(String)
    stats_access = Column(Boolean, default=False)
    description = Column(String, nullable=True)

    user_subscriptions = relationship("UserSubscription", back_populates="subscription", cascade="all, delete-orphan")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    subscription = relationship("Subscription", back_populates="user_subscriptions")
    payment = relationship("Payment", backref="user_subscription")

