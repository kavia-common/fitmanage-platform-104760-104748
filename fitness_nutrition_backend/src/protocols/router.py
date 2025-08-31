from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.utils import pagination_params, paginate, assert_client_ownership_or_admin
from src.core.database import get_db
from src.core.security import get_current_user
from src.models import ProtocolGoal, GoalProgress, User
from src.schemas.protocols import (
    ProtocolGoalCreate,
    ProtocolGoalRead,
    GoalProgressCreate,
    GoalProgressRead,
)

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=list[ProtocolGoalRead],
    summary="List protocol goals",
    description="List protocol goals with pagination and ownership checks.",
)
def list_protocol_goals(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    offset_limit: tuple[int, int] = Depends(pagination_params),
):
    offset, limit = offset_limit
    role_names = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in role_names or "professional" in role_names

    q = db.query(ProtocolGoal)
    if not is_admin_or_pro:
        from src.models import Client
        q = q.join(ProtocolGoal.client).filter(Client.user_id == current.id)
    return paginate(q.order_by(ProtocolGoal.id.desc()), offset, limit)


# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=ProtocolGoalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create protocol goal",
    description="Create a protocol/goal for a client (ownership enforced).",
)
def create_protocol_goal(
    payload: ProtocolGoalCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    assert_client_ownership_or_admin(db, payload.client_id, current, "Cannot create goal for this client")
    obj = ProtocolGoal(
        client_id=payload.client_id,
        type=payload.type,
        title=payload.title,
        target_value=payload.target_value,
        unit=payload.unit,
        notes=payload.notes,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.get(
    "/{goal_id}",
    response_model=ProtocolGoalRead,
    summary="Get protocol goal",
    description="Get a protocol/goal by ID (ownership enforced).",
)
def get_protocol_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    obj = db.get(ProtocolGoal, goal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Protocol goal not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)
    return obj


# PUBLIC_INTERFACE
@router.put(
    "/{goal_id}",
    response_model=ProtocolGoalRead,
    summary="Update protocol goal",
    description="Update a protocol/goal (ownership enforced).",
)
def update_protocol_goal(
    goal_id: int,
    payload: ProtocolGoalCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    obj = db.get(ProtocolGoal, goal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Protocol goal not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)

    obj.type = payload.type
    obj.title = payload.title
    obj.target_value = payload.target_value
    obj.unit = payload.unit
    obj.notes = payload.notes
    obj.start_date = payload.start_date
    obj.end_date = payload.end_date
    if payload.client_id != obj.client_id:
        assert_client_ownership_or_admin(db, payload.client_id, current, "Cannot move goal to this client")
        obj.client_id = payload.client_id
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete protocol goal",
    description="Delete a protocol/goal (ownership enforced).",
)
def delete_protocol_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    obj = db.get(ProtocolGoal, goal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Protocol goal not found")
    assert_client_ownership_or_admin(db, obj.client_id, current)
    db.delete(obj)
    db.commit()
    return None


# ------- Progress endpoints -------

# PUBLIC_INTERFACE
@router.get(
    "/{goal_id}/progress",
    response_model=list[GoalProgressRead],
    summary="List progress for a goal",
    description="List progress entries for a protocol/goal (ownership enforced).",
)
def list_progress(
    goal_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    offset_limit: tuple[int, int] = Depends(pagination_params),
):
    goal = db.get(ProtocolGoal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Protocol goal not found")
    assert_client_ownership_or_admin(db, goal.client_id, current)
    offset, limit = offset_limit
    q = db.query(GoalProgress).filter(GoalProgress.goal_id == goal_id).order_by(GoalProgress.id.desc())
    return paginate(q, offset, limit)


# PUBLIC_INTERFACE
@router.post(
    "/{goal_id}/progress",
    response_model=GoalProgressRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create progress point",
    description="Add a progress measurement to a protocol/goal (ownership enforced).",
)
def create_progress(
    goal_id: int,
    payload: GoalProgressCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    goal = db.get(ProtocolGoal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Protocol goal not found")
    assert_client_ownership_or_admin(db, goal.client_id, current)

    obj = GoalProgress(goal_id=goal_id, date=payload.date, value=payload.value, notes=payload.notes)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.delete(
    "/{goal_id}/progress/{progress_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete progress point",
    description="Delete a progress entry from a protocol/goal (ownership enforced).",
)
def delete_progress(
    goal_id: int,
    progress_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    goal = db.get(ProtocolGoal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Protocol goal not found")
    assert_client_ownership_or_admin(db, goal.client_id, current)

    obj = db.get(GoalProgress, progress_id)
    if not obj or obj.goal_id != goal_id:
        raise HTTPException(status_code=404, detail="Progress entry not found")
    db.delete(obj)
    db.commit()
    return None
