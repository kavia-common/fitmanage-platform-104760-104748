from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

from src.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that the plaintext matches the given hash."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create a signed JWT access token.

    Args:
        subject: The subject (sub) claim, typically user ID or email.
        expires_delta: Optional timedelta for expiry. Defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES.
        extra_claims: Additional claims to embed in the token.

    Returns:
        Encoded JWT as string.
    """
    settings = get_settings()
    to_encode: Dict[str, Any] = extra_claims.copy() if extra_claims else {}
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "nbf": now,
            "sub": str(subject),
        }
    )
    if settings.JWT_ISSUER:
        to_encode["iss"] = settings.JWT_ISSUER
    if settings.JWT_AUDIENCE:
        to_encode["aud"] = settings.JWT_AUDIENCE

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
