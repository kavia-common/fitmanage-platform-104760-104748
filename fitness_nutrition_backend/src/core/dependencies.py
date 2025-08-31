from typing import List

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.core.security import get_current_user
from src.models import User
from src.services.subscriptions import (
    ensure_within_limits_clients,
    ensure_within_limits_diet_plans,
    ensure_within_limits_workout_plans,
)


def _normalize_cors_origins(origins: List[str] | List) -> List[str]:
    # Allow strings with comma-separated origins as well
    if isinstance(origins, list):
        return [str(o).strip() for o in origins]
    if isinstance(origins, str):
        return [o.strip() for o in origins.split(",")]
    return []


# PUBLIC_INTERFACE
def setup_cors(app: FastAPI) -> None:
    """Attach CORS middleware according to settings.

    Args:
        app: FastAPI application instance.
    """
    settings = get_settings()
    origins = _normalize_cors_origins(settings.BACKEND_CORS_ORIGINS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ---- Plan limitation dependencies (to be reused in routers) ----

# PUBLIC_INTERFACE
def require_can_create_client(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    """Dependency to enforce plan limits when creating a client."""
    ensure_within_limits_clients(db, current)


# PUBLIC_INTERFACE
def require_can_create_workout_for_client(
    client_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    """Dependency to enforce workout plan limits per client."""
    ensure_within_limits_workout_plans(db, current.id, client_id)


# PUBLIC_INTERFACE
def require_can_create_diet_for_client(
    client_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    """Dependency to enforce diet plan limits per client."""
    ensure_within_limits_diet_plans(db, current.id, client_id)
