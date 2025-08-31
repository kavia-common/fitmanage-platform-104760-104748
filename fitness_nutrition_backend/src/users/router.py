from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List users")
def list_users():
    """List users placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.get("/{user_id}", summary="Get user by ID")
def get_user(user_id: str):
    """Get a single user placeholder."""
    return {"id": user_id}
