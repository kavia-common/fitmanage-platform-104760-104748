from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List diet plans")
def list_diet_plans():
    """List diet plans placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create diet plan")
def create_diet_plan():
    """Create diet plan placeholder."""
    return {"message": "created"}
