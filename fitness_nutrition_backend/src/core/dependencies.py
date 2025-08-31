from typing import List

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from src.core.config import get_settings


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
