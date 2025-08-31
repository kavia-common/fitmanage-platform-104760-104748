from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List reports")
def list_reports(db: Session = Depends(get_db)):
    """List reports placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.get("/summary", summary="Summary report")
def summary_report(db: Session = Depends(get_db)):
    """Summary report placeholder."""
    return {"summary": {}}
