from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

# Association table for User<->Role many-to-many
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)


class Role(Base):
    """Role entity for RBAC scopes like 'user', 'professional', 'gym', 'admin'."""
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        passive_deletes=True,
    )


class User(Base):
    """User entity with authentication details and profile basics."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles: Mapped[List[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        passive_deletes=True,
        lazy="joined",
    )
