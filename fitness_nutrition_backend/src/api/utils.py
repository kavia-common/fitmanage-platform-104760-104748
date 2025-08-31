from typing import Any, Optional, Tuple

from fastapi import HTTPException, Query, status
from sqlalchemy.orm import Query as SAQuery
from sqlalchemy.orm import Session

from src.models import Client, User


# PUBLIC_INTERFACE
def pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)."),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)."),
) -> Tuple[int, int]:
    """Return offset and limit from page parameters."""
    offset = (page - 1) * page_size
    return offset, page_size


def _apply_pagination(q: SAQuery, offset: int, limit: int) -> SAQuery:
    return q.offset(offset).limit(limit)


# PUBLIC_INTERFACE
def paginate(q: SAQuery, offset: int, limit: int) -> list[Any]:
    """Apply pagination on a SQLAlchemy query and return items."""
    return _apply_pagination(q, offset, limit).all()


# PUBLIC_INTERFACE
def assert_client_ownership_or_admin(
    db: Session, client_id: int, current: User, error_message: Optional[str] = None
) -> Client:
    """Ensure the current user is allowed to access the given client.

    - Admins and professionals can access all clients.
    - Regular users can only access clients which are linked to their user_id (self).
    """
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    role_names = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in role_names or "professional" in role_names
    if is_admin_or_pro:
        return client

    # Regular user must own the client record
    if client.user_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message or "Not authorized to access this client",
        )
    return client
