from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models import User
from src.reports.service import get_activity_trends, get_clients_breakdown, get_entity_counts

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    summary="List reports",
    description="List available report groups for the caller.",
)
def list_reports(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return available report group identifiers."""
    return {"items": ["summary", "trends", "clients-breakdown"]}


# PUBLIC_INTERFACE
@router.get(
    "/summary",
    summary="Summary report",
    description="Return high-level counts for clients, workout/diet plans, and protocols.",
)
def summary_report(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return aggregate counts of main entities with ownership checks."""
    role_names = {r.name for r in (current.roles or [])}
    data = get_entity_counts(db, current.id, role_names)
    return {"summary": data}


# PUBLIC_INTERFACE
@router.get(
    "/trends",
    summary="Activity trends",
    description="Return workout logs and diet entries counts grouped by day for the last N days.",
)
def trends_report(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return time series trends for activity in the recent period."""
    role_names = {r.name for r in (current.roles or [])}
    data = get_activity_trends(db, current.id, role_names, days=days)
    return {"trends": data}


# PUBLIC_INTERFACE
@router.get(
    "/clients-breakdown",
    summary="Per-client plan breakdown",
    description="Return counts of workout and diet plans per client for the caller.",
)
def clients_breakdown(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return per-client plan counts."""
    role_names = {r.name for r in (current.roles or [])}
    data = get_clients_breakdown(db, current.id, role_names)
    return data
