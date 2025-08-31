from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List reports")
def list_reports():
    """List reports placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.get("/summary", summary="Summary report")
def summary_report():
    """Summary report placeholder."""
    return {"summary": {}}
