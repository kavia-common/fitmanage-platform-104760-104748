from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ProtocolGoal(Base):
    """Target protocol/goal configuration for a client (e.g., weight, performance)."""
    __tablename__ = "protocol_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50))  # e.g., weight, calories, custom
    title: Mapped[str] = mapped_column(String(255))
    target_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text)

    start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    client = relationship("Client", lazy="joined")
    progress_points = relationship("GoalProgress", cascade="all, delete-orphan", back_populates="goal")


class GoalProgress(Base):
    """Periodic progress measurements toward a goal."""
    __tablename__ = "goal_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("protocol_goals.id", ondelete="CASCADE"))
    date: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    goal = relationship("ProtocolGoal", back_populates="progress_points")
