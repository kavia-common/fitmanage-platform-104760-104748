from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Subscription(Base):
    """User subscription details for plans/tiers."""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    plan: Mapped[str] = mapped_column(String(50))  # e.g., basic, pro, enterprise
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    start_date: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", lazy="joined")
