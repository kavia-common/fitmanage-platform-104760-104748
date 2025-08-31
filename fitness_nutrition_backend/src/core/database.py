from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session

from src.core.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base for ORM models."""
    pass


def _create_engine():
    """Create SQLAlchemy engine from settings."""
    settings = get_settings()
    url = settings.DATABASE_URL
    connect_args = {}
    # SQLite needs check_same_thread disabled for multithreading when using file/db
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, echo=settings.SQL_ECHO, future=True, connect_args=connect_args)


# Global engine and session factory
engine = _create_engine()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True))


# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Yield a database session for FastAPI dependencies.

    Yields:
        Session: SQLAlchemy session, closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator:
    """Context manager to use DB session in scripts/background tasks."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
