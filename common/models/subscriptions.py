# common/models/subscriptions.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey,
    UniqueConstraint, Index, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False)
    language = Column(String(5), nullable=False, default="ru")   # NOT NULL + default
    name = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    product_limit = Column(Integer, default=0)
    promo_balance = Column(Integer, default=0)
    support_level = Column(String(50))
    stats_access = Column(Boolean, default=False)
    description = Column(Text)  # явный TEXT

    __table_args__ = (
        UniqueConstraint("code", "language", name="uq_code_language"),
        Index("ix_subscriptions_name", "name"),
    )

    # внутренняя связь (в рамках сервиса подписок)
    user_subscriptions = relationship(
        "UserSubscription",
        back_populates="subscription",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    # без внешних FK на чужие сервисы
    user_id = Column(Integer, nullable=False, index=True)  # нет FK на users
    payment_id = Column(Integer, nullable=True)            # нет FK на payments

    # внутренняя FK — на свою таблицу subscriptions
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    auto_renew = Column(Boolean, default=False)

    # внутренняя двусторонняя связь
    subscription = relationship(
        "Subscription",
        back_populates="user_subscriptions",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_user_subscriptions_user_active", "user_id", "is_active"),
        Index("ix_user_subscriptions_subscription", "subscription_id"),
    )