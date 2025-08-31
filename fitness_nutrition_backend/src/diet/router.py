from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List diet plans")
def list_diet_plans(db: Session = Depends(get_db)):
    """List diet plans placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create diet plan")
def create_diet_plan(db: Session = Depends(get_db)):
    """Create diet plan placeholder."""
    return {"message": "created"}
