from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import create_access_token, get_password_hash, verify_password
from src.models import User, Role
from src.schemas.user import UserCreate, UserLogin, Token, UserRead

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate a user and return a JWT access token. Use the token as 'Authorization: Bearer <token>' in subsequent requests.",
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=60))
    return Token(access_token=access_token)


# PUBLIC_INTERFACE
@router.post("/register", response_model=UserRead, summary="Register", description="Register a new user with default 'user' role.")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with default 'user' role."""
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = get_password_hash(payload.password)
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=hashed, is_active=True)
    # ensure default role exists
    role = db.query(Role).filter(Role.name == "user").first()
    if not role:
        role = Role(name="user", description="Default role")
        db.add(role)
        db.flush()
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
