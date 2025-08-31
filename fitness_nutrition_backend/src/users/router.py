from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models import User
from src.schemas.user import UserRead

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", response_model=list[UserRead], summary="List users")
def list_users(db: Session = Depends(get_db)):
    """List users from the database."""
    return db.query(User).all()


# PUBLIC_INTERFACE
@router.get("/{user_id}", response_model=UserRead, summary="Get user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
