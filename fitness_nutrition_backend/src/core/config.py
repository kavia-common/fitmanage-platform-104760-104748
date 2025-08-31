from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings loaded from environment variables.

    Note: Do not hard-code secrets. Provide them via environment variables.
    You may create a .env.example to document required variables.
    """
    # App
    APP_NAME: str = Field(default="Fitness & Nutrition API", description="Application visible name for docs/UI.")
    APP_DESCRIPTION: str = Field(
        default="REST API for fitness and nutrition management with modular domains.",
        description="OpenAPI description text."
    )
    APP_VERSION: str = Field(default="0.1.0", description="Semantic version.")
    ENV: str = Field(default="development", description="Environment name (development/staging/production).")

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] | List[str] = Field(
        default_factory=lambda: ["http://localhost", "http://localhost:3000", "http://localhost:5173"],
        description="Allowed origins for CORS."
    )

    # Security (placeholders for future JWT implementation)
    SECRET_KEY: str = Field(default="change-me-in-env", description="Secret key for cryptographic operations.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="JWT access token expiry in minutes.")
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm.")

    # WebSocket base path (for future use)
    WEBSOCKET_BASE_PATH: str = Field(default="/ws", description="Base path for websocket endpoints.")

    class Config:
        env_file = ".env"
        case_sensitive = True


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: The Settings instance loaded from environment variables.
    """
    return Settings()
