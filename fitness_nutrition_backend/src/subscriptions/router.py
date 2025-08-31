from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models import Subscription, User
from src.schemas.subscription import SubscriptionRead
from src.services.subscriptions import payment_provider, get_active_subscription

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=list[SubscriptionRead],
    summary="List subscriptions",
    description="List your subscriptions (active and inactive).",
)
def list_subscriptions(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """List subscriptions for current user."""
    return db.query(Subscription).filter(Subscription.user_id == current.id).order_by(Subscription.id.desc()).all()


from src.schemas.subscriptions_requests import SubscriptionPlanRequest


# PUBLIC_INTERFACE
@router.post(
    "/checkout",
    summary="Create checkout session (stub)",
    description="Returns a stubbed payment checkout URL and session id.",
)
def create_checkout(
    payload: SubscriptionPlanRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Return a stub checkout link for the requested plan."""
    if not payload.plan:
        raise HTTPException(status_code=400, detail="Plan is required")
    return payment_provider.create_checkout_session(current, payload.plan)


# PUBLIC_INTERFACE
@router.post(
    "/activate",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Activate subscription (stub)",
    description="Activate a subscription locally (simulates provider webhook).",
)
def activate_subscription(
    payload: SubscriptionPlanRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Activate a subscription using the stub payment provider."""
    if not payload.plan:
        raise HTTPException(status_code=400, detail="Plan is required")
    # Deactivate any existing active sub
    sub = get_active_subscription(db, current.id)
    if sub:
        sub.is_active = False
        db.add(sub)
        db.commit()
    # Create a new active sub
    sub = payment_provider.activate_subscription(db, current, payload.plan)
    return sub


# PUBLIC_INTERFACE
@router.post(
    "/cancel",
    summary="Cancel subscription (stub)",
    description="Cancel active subscription for current user.",
)
def cancel_subscription(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Cancel current active subscription."""
    payment_provider.cancel_subscription(db, current)
    return {"status": "canceled"}
