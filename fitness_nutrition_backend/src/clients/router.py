from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List clients")
def list_clients(db: Session = Depends(get_db)):
    """List clients placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create client")
def create_client(db: Session = Depends(get_db)):
    """Create client placeholder."""
    return {"message": "created"}
