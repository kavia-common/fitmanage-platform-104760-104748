from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class WorkoutPlan(Base):
    """Workout plan describing scheduled exercises for a client."""
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", lazy="joined")
    exercises = relationship("WorkoutExercise", cascade="all, delete-orphan", back_populates="plan")


class WorkoutExercise(Base):
    """Exercise details within a workout plan."""
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("workout_plans.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    sets: Mapped[int] = mapped_column(Integer, default=3)
    reps: Mapped[int] = mapped_column(Integer, default=10)
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text)

    plan = relationship("WorkoutPlan", back_populates="exercises")


class WorkoutLog(Base):
    """Logs of performed exercises during a workout session."""
    __tablename__ = "workout_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("workout_plans.id", ondelete="SET NULL"), nullable=True)
    date: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)

    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    client = relationship("Client", lazy="joined")
    plan = relationship("WorkoutPlan", lazy="joined")
