from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class FoodItem(Base):
    """Food item with nutrition data."""
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    calories: Mapped[int] = mapped_column(Integer, default=0)
    protein_g: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    carbs_g: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    fats_g: Mapped[float] = mapped_column(Numeric(6, 2), default=0)


class DietPlan(Base):
    """Diet plan assigned to a client."""
    __tablename__ = "diet_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", lazy="joined")
    entries = relationship("DietEntry", cascade="all, delete-orphan", back_populates="plan")


class DietEntry(Base):
    """Diet entries referencing food items consumed in a day."""
    __tablename__ = "diet_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("diet_plans.id", ondelete="CASCADE"))
    food_item_id: Mapped[int] = mapped_column(ForeignKey("food_items.id", ondelete="RESTRICT"))
    date: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    quantity: Mapped[float] = mapped_column(Numeric(8, 2), default=1.0)
    meal_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # breakfast/lunch/dinner/snack

    plan = relationship("DietPlan", back_populates="entries")
    food_item = relationship("FoodItem", lazy="joined")
