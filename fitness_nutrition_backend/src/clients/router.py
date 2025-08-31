from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List clients")
def list_clients():
    """List clients placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create client")
def create_client():
    """Create client placeholder."""
    return {"message": "created"}
