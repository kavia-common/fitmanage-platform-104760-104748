from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List notifications")
def list_notifications(db: Session = Depends(get_db)):
    """List notifications placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create notification")
def create_notification(db: Session = Depends(get_db)):
    """Create notification placeholder."""
    return {"message": "created"}
