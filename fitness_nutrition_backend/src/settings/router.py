from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session

from src.core.database import get_db, Base
from src.core.security import get_current_user
from src.models import User

router = APIRouter()


class Preferences(BaseModel):
    theme: Optional[str] = Field(default="light", description="UI theme, e.g., light/dark")
    notifications_enabled: bool = Field(default=True, description="Enable in-app notifications")
    locale: Optional[str] = Field(default=None, description="Preferred locale/language code")


class SettingsRead(BaseModel):
    user_id: int
    preferences: Preferences


class SettingsUpdate(BaseModel):
    preferences: Preferences


# Implement a simple Settings table if not present in migrations.
# This uses SQLAlchemy metadata to allow runtime table creation in dev; production should add an Alembic migration.
class UserSettings(Base):
    __tablename__ = "user_settings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    data = Column(JSON, nullable=False, default={})
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_settings_user"),)


def _get_or_create_user_settings(db: Session, user_id: int) -> UserSettings:
    obj: UserSettings | None = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if obj:
        return obj
    obj = UserSettings(user_id=user_id, data={})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=SettingsRead,
    summary="Get my settings",
    description="Get preferences for the current user.",
)
def get_my_settings(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Return settings for current user, creating defaults if none exist."""
    obj = _get_or_create_user_settings(db, current.id)
    prefs = Preferences(**(obj.data or {}))
    return {"user_id": current.id, "preferences": prefs}


# PUBLIC_INTERFACE
@router.put(
    "/me",
    response_model=SettingsRead,
    summary="Update my settings",
    description="Update preferences for the current user.",
)
def update_my_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Update current user's settings and return the new record."""
    obj = _get_or_create_user_settings(db, current.id)
    obj.data = payload.preferences.model_dump()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"user_id": current.id, "preferences": Preferences(**(obj.data or {}))}
