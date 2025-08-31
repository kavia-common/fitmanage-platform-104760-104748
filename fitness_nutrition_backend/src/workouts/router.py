from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List workouts")
def list_workouts(db: Session = Depends(get_db)):
    """List workouts placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create workout")
def create_workout(db: Session = Depends(get_db)):
    """Create workout placeholder."""
    return {"message": "created"}
