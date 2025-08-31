from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.utils import pagination_params, paginate, assert_client_ownership_or_admin
from src.core.database import get_db
from src.core.security import get_current_user
from src.models import DietPlan, User
from src.schemas.diet import DietPlanCreate, DietPlanRead

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=list[DietPlanRead],
    summary="List diet plans",
    description="List diet plans with pagination. Admin/pro can view all; regular users only those belonging to their clients.",
)
def list_diet_plans(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    offset_limit: tuple[int, int] = Depends(pagination_params),
):
    """List diet plans with ownership checks."""
    offset, limit = offset_limit
    role_names = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in role_names or "professional" in role_names

    q = db.query(DietPlan)
    if not is_admin_or_pro:
        from src.models import Client
        q = q.join(DietPlan.client).filter(Client.user_id == current.id)
    items = paginate(q.order_by(DietPlan.id.desc()), offset, limit)
    return items


# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=DietPlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create diet plan",
    description="Create a diet plan for a client (ownership enforced).",
)
def create_diet_plan(
    payload: DietPlanCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Create a diet plan after verifying client ownership."""
    assert_client_ownership_or_admin(db, payload.client_id, current, "Cannot create plan for this client")
    obj = DietPlan(
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
    response_model=DietPlanRead,
    summary="Get diet plan",
    description="Get a diet plan by ID with ownership checks.",
)
def get_diet_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Get a diet plan with ownership check."""
    obj = db.get(DietPlan, plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)
    return obj


# PUBLIC_INTERFACE
@router.put(
    "/{plan_id}",
    response_model=DietPlanRead,
    summary="Update diet plan",
    description="Update a diet plan (ownership enforced).",
)
def update_diet_plan(
    plan_id: int,
    payload: DietPlanCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Update a diet plan after verifying ownership."""
    obj = db.get(DietPlan, plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)

    obj.title = payload.title
    obj.description = payload.description
    obj.start_date = payload.start_date
    obj.end_date = payload.end_date
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
    summary="Delete diet plan",
    description="Delete a diet plan (ownership enforced).",
)
def delete_diet_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Delete a diet plan after verifying ownership."""
    obj = db.get(DietPlan, plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)
    db.delete(obj)
    db.commit()
    return None
