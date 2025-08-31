from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict

from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

from src.models import (
    Client,
    DietEntry,
    DietPlan,
    ProtocolGoal,
    WorkoutLog,
    WorkoutPlan,
)


def _default_date_range(days: int = 30) -> tuple[date, date]:
    """Return a (start_date, end_date) inclusive range for recent days."""
    end = date.today()
    start = end - timedelta(days=days - 1)
    return start, end


# PUBLIC_INTERFACE
def get_entity_counts(db: Session, current_user_id: int, role_names: set[str]) -> Dict[str, int]:
    """Return high-level counts for key entities with ownership rules applied.

    - Admin/professional can see all.
    - Regular users see only their clients' related entities.
    """
    is_admin_or_pro = ("admin" in role_names) or ("professional" in role_names)

    def _count(query):
        return query.scalar() or 0

    if is_admin_or_pro:
        clients = _count(db.query(func.count(Client.id)))
        workouts = _count(db.query(func.count(WorkoutPlan.id)))
        diets = _count(db.query(func.count(DietPlan.id)))
        protocols = _count(db.query(func.count(ProtocolGoal.id)))
    else:
        # Join through client ownership
        clients = _count(db.query(func.count(Client.id)).filter(Client.user_id == current_user_id))
        workouts = _count(
            db.query(func.count(WorkoutPlan.id))
            .join(Client, Client.id == WorkoutPlan.client_id)
            .filter(Client.user_id == current_user_id)
        )
        diets = _count(
            db.query(func.count(DietPlan.id))
            .join(Client, Client.id == DietPlan.client_id)
            .filter(Client.user_id == current_user_id)
        )
        protocols = _count(
            db.query(func.count(ProtocolGoal.id))
            .join(Client, Client.id == ProtocolGoal.client_id)
            .filter(Client.user_id == current_user_id)
        )

    return {
        "clients": clients,
        "workout_plans": workouts,
        "diet_plans": diets,
        "protocol_goals": protocols,
    }


# PUBLIC_INTERFACE
def get_activity_trends(db: Session, current_user_id: int, role_names: set[str], days: int = 30) -> Dict[str, Any]:
    """Return activity trends for the past N days for workout logs and diet entries.

    Data grouped by date with counts.
    """
    start_date, end_date = _default_date_range(days)
    is_admin_or_pro = ("admin" in role_names) or ("professional" in role_names)

    # Workout logs trend
    wl_q = db.query(
        cast(WorkoutLog.date, Date).label("d"),
        func.count(WorkoutLog.id).label("c"),
    )
    if not is_admin_or_pro:
        wl_q = wl_q.join(Client, Client.id == WorkoutLog.client_id).filter(Client.user_id == current_user_id)
    wl_q = wl_q.filter(
        cast(WorkoutLog.date, Date) >= start_date,
        cast(WorkoutLog.date, Date) <= end_date,
    ).group_by("d").order_by("d")

    workout_logs = [{"date": d.isoformat() if isinstance(d, (date, datetime)) else str(d), "count": int(c)} for d, c in wl_q.all()]

    # Diet entries trend
    de_q = db.query(
        cast(DietEntry.date, Date).label("d"),
        func.count(DietEntry.id).label("c"),
    )
    if not is_admin_or_pro:
        de_q = de_q.join(DietPlan, DietPlan.id == DietEntry.plan_id).join(Client, Client.id == DietPlan.client_id).filter(
            Client.user_id == current_user_id
        )
    de_q = de_q.filter(
        cast(DietEntry.date, Date) >= start_date,
        cast(DietEntry.date, Date) <= end_date,
    ).group_by("d").order_by("d")

    diet_entries = [{"date": d.isoformat() if isinstance(d, (date, datetime)) else str(d), "count": int(c)} for d, c in de_q.all()]

    return {
        "workout_logs": workout_logs,
        "diet_entries": diet_entries,
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
    }


# PUBLIC_INTERFACE
def get_clients_breakdown(db: Session, current_user_id: int, role_names: set[str]) -> Dict[str, Any]:
    """Return per-client breakdown of numbers of workout and diet plans."""
    is_admin_or_pro = ("admin" in role_names) or ("professional" in role_names)

    client_q = db.query(Client)
    if not is_admin_or_pro:
        client_q = client_q.filter(Client.user_id == current_user_id)
    clients = client_q.all()

    breakdown: list[dict[str, Any]] = []
    for c in clients:
        workout_count = (
            db.query(func.count(WorkoutPlan.id))
            .filter(WorkoutPlan.client_id == c.id)
            .scalar()
            or 0
        )
        diet_count = (
            db.query(func.count(DietPlan.id))
            .filter(DietPlan.client_id == c.id)
            .scalar()
            or 0
        )
        breakdown.append(
            {
                "client_id": c.id,
                "display_name": c.display_name,
                "workout_plans": int(workout_count),
                "diet_plans": int(diet_count),
            }
        )
    return {"items": breakdown}
