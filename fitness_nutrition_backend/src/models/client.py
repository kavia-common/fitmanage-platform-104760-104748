from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Client(Base):
    """Client represents a person managed by a professional or gym."""
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    display_name: Mapped[str] = mapped_column(String(255))
    date_of_birth: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", lazy="joined")
