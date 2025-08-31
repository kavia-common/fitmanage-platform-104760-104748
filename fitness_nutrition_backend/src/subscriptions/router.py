from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List subscriptions")
def list_subscriptions(db: Session = Depends(get_db)):
    """List subscriptions placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create subscription")
def create_subscription(db: Session = Depends(get_db)):
    """Create subscription placeholder."""
    return {"message": "created"}
