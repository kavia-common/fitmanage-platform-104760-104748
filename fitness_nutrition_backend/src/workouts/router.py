from fastapi import APIRouter

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", summary="List workouts")
def list_workouts():
    """List workouts placeholder."""
    return {"items": []}


# PUBLIC_INTERFACE
@router.post("/", summary="Create workout")
def create_workout():
    """Create workout placeholder."""
    return {"message": "created"}
