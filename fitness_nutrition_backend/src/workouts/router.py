from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.utils import pagination_params, paginate, assert_client_ownership_or_admin
from src.core.database import get_db
from src.core.security import get_current_user
from src.models import WorkoutPlan, User
from src.schemas.workout import WorkoutPlanCreate, WorkoutPlanRead
from src.services.subscriptions import ensure_within_limits_workout_plans

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=list[WorkoutPlanRead],
    summary="List workouts",
    description="List workout plans with pagination. Admin/pro can view all; regular users only those belonging to their clients.",
)
def list_workouts(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    offset_limit: tuple[int, int] = Depends(pagination_params),
):
    """List workout plans with ownership checks."""
    offset, limit = offset_limit
    role_names = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in role_names or "professional" in role_names

    q = db.query(WorkoutPlan)
    if not is_admin_or_pro:
        # Join via relationship attribute loaded, but simple filter on joined client
        from src.models import Client  # local import to avoid cycles
        q = q.join(WorkoutPlan.client).filter(Client.user_id == current.id)
    items = paginate(q.order_by(WorkoutPlan.id.desc()), offset, limit)
    return items


# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=WorkoutPlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create workout",
    description="Create a workout plan for a client (ownership enforced).",
)
def create_workout(
    payload: WorkoutPlanCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Create a workout plan after verifying client ownership."""
    # Ensure ownership
    assert_client_ownership_or_admin(db, payload.client_id, current, "Cannot create plan for this client")
    # Enforce per-plan limits if the client belongs to the current user (non-admin/pro)
    ensure_within_limits_workout_plans(db, current.id, payload.client_id)

    obj = WorkoutPlan(
        client_id=payload.client_id,
        title=payload.title,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.get(
    "/{plan_id}",
    response_model=WorkoutPlanRead,
    summary="Get workout plan",
    description="Get a workout plan by ID with ownership checks.",
)
def get_workout(
    plan_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Get a workout plan with ownership check."""
    obj = db.get(WorkoutPlan, plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)
    return obj


# PUBLIC_INTERFACE
@router.put(
    "/{plan_id}",
    response_model=WorkoutPlanRead,
    summary="Update workout plan",
    description="Update a workout plan (ownership enforced).",
)
def update_workout(
    plan_id: int,
    payload: WorkoutPlanCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Update a workout plan after verifying ownership."""
    obj = db.get(WorkoutPlan, plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)

    obj.title = payload.title
    obj.description = payload.description
    obj.start_date = payload.start_date
    obj.end_date = payload.end_date
    # Allow moving to another owned client
    if payload.client_id != obj.client_id:
        assert_client_ownership_or_admin(db, payload.client_id, current, "Cannot move plan to this client")
        obj.client_id = payload.client_id

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workout plan",
    description="Delete a workout plan (ownership enforced).",
)
def delete_workout(
    plan_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Delete a workout plan after verifying ownership."""
    obj = db.get(WorkoutPlan, plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)
    db.delete(obj)
    db.commit()
    return None
