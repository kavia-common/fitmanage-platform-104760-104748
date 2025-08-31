from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List subscriptions")
def list_subscriptions():
    """List subscriptions placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create subscription")
def create_subscription():
    """Create subscription placeholder."""
    return {"message": "created"}
