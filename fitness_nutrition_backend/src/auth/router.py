from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("/login", summary="Login")
def login():
    """Login endpoint placeholder. Expects credentials; returns token (to be implemented)."""
    return {"message": "login stub"}


# PUBLIC_INTERFACE
@router.post("/register", summary="Register")
def register():
    """Register a new user placeholder. To be implemented."""
    return {"message": "register stub"}
