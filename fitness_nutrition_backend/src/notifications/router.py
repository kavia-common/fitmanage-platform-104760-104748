from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List notifications")
def list_notifications():
    """List notifications placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create notification")
def create_notification():
    """Create notification placeholder."""
    return {"message": "created"}
