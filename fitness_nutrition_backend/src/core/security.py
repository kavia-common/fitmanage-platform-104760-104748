from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 bearer token support (Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that the plaintext matches the given hash."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
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


# PUBLIC_INTERFACE
def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT, returning its claims or raising an HTTPException."""
    settings = get_settings()
    try:
        claims = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], audience=settings.JWT_AUDIENCE)
        return claims
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI dependency: resolve and return the current authenticated User from bearer token."""
    claims = decode_token(token)
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = db.get(User, int(sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


# PUBLIC_INTERFACE
def require_roles(*required: str):
    """Dependency factory to enforce that current user has at least one of the required roles.

    Usage:
        @router.get(..., dependencies=[Depends(require_roles('admin', 'professional'))])
    """
    def _dependency(user: User = Depends(get_current_user)) -> User:
        role_names = {r.name for r in (user.roles or [])}
        if "admin" in role_names:
            return user  # admins bypass
        if not required or role_names.intersection(set(required)):
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return _dependency
