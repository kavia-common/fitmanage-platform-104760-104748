from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models import Subscription, User


@dataclass
class PlanLimits:
    """Defines feature and quota limits per subscription plan."""
    max_clients: int
    max_workout_plans_per_client: int
    max_diet_plans_per_client: int
    # Future: API call limits, storage, notifications quota, etc.


# PUBLIC_INTERFACE
def get_plan_limits(plan: str) -> PlanLimits:
    """Return plan limits by plan id/name."""
    normalized = (plan or "").lower()
    if normalized in {"pro", "professional"}:
        return PlanLimits(max_clients=200, max_workout_plans_per_client=50, max_diet_plans_per_client=50)
    if normalized in {"basic", "starter"}:
        return PlanLimits(max_clients=10, max_workout_plans_per_client=5, max_diet_plans_per_client=5)
    # Default/fallback plan
    return PlanLimits(max_clients=3, max_workout_plans_per_client=2, max_diet_plans_per_client=2)


# PUBLIC_INTERFACE
def get_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """Return active subscription for a user, if exists."""
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.is_active == True)  # noqa: E712
        .order_by(Subscription.id.desc())
        .first()
    )


# PUBLIC_INTERFACE
def ensure_within_limits_clients(db: Session, owner: User) -> None:
    """Validate if owner can create another client according to plan."""
    sub = get_active_subscription(db, owner.id)
    plan = sub.plan if sub else "free"
    limits = get_plan_limits(plan)

    from src.models import Client
    count = db.query(Client).filter(Client.user_id == owner.id).count()
    if count >= limits.max_clients:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Client limit reached for plan '{plan}'. Max allowed: {limits.max_clients}",
        )


# PUBLIC_INTERFACE
def ensure_within_limits_workout_plans(db: Session, owner_user_id: int, client_id: int) -> None:
    """Validate workout plan creation limit per client for owner's plan."""
    sub = get_active_subscription(db, owner_user_id)
    plan = sub.plan if sub else "free"
    limits = get_plan_limits(plan)

    from src.models import WorkoutPlan, Client
    # Verify ownership
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client or client.user_id != owner_user_id:
        # For admins/pro we'll skip limit by ownership; limits apply to owner accounts
        return
    count = db.query(WorkoutPlan).filter(WorkoutPlan.client_id == client_id).count()
    if count >= limits.max_workout_plans_per_client:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Workout plan limit reached for plan '{plan}'. Max: {limits.max_workout_plans_per_client}",
        )


# PUBLIC_INTERFACE
def ensure_within_limits_diet_plans(db: Session, owner_user_id: int, client_id: int) -> None:
    """Validate diet plan creation limit per client for owner's plan."""
    sub = get_active_subscription(db, owner_user_id)
    plan = sub.plan if sub else "free"
    limits = get_plan_limits(plan)

    from src.models import DietPlan, Client
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client or client.user_id != owner_user_id:
        return
    count = db.query(DietPlan).filter(DietPlan.client_id == client_id).count()
    if count >= limits.max_diet_plans_per_client:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Diet plan limit reached for plan '{plan}'. Max: {limits.max_diet_plans_per_client}",
        )


# ----- Stub Payment Provider -----

class PaymentError(Exception):
    """Error raised by payment provider stubs."""


class PaymentProviderStub:
    """A stubbed payment provider for creating, canceling, and verifying subscriptions."""

    # PUBLIC_INTERFACE
    def create_checkout_session(self, user: User, plan: str) -> dict:
        """Simulate provider checkout session creation and return a fake session link/id."""
        return {
            "checkout_url": f"https://payments.example/checkout?user={user.id}&plan={plan}",
            "session_id": f"sess_{user.id}_{plan}",
        }

    # PUBLIC_INTERFACE
    def activate_subscription(self, db: Session, user: User, plan: str) -> Subscription:
        """Activate a subscription locally as if provider succeeded."""
        sub = Subscription(
            user_id=user.id,
            plan=plan,
            price=0,
            currency="USD",
            start_date=date.today(),
            end_date=None,
            is_active=True,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub

    # PUBLIC_INTERFACE
    def cancel_subscription(self, db: Session, user: User) -> None:
        """Cancel latest active subscription locally."""
        sub = get_active_subscription(db, user.id)
        if sub:
            sub.is_active = False
            db.add(sub)
            db.commit()


payment_provider = PaymentProviderStub()
