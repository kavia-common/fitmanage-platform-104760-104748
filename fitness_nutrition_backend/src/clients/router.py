from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.utils import pagination_params, paginate, assert_client_ownership_or_admin
from src.core.database import get_db
from src.core.security import get_current_user
from src.models import Client, User
from src.schemas.client import ClientCreate, ClientRead
from src.services.subscriptions import ensure_within_limits_clients

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=list[ClientRead],
    summary="List clients",
    description="List clients with pagination. Admin/pro can list all; regular users see only their own client record(s).",
)
def list_clients(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    offset_limit: tuple[int, int] = Depends(pagination_params),
):
    """List clients with pagination and ownership checks."""
    offset, limit = offset_limit
    role_names = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in role_names or "professional" in role_names

    q = db.query(Client)
    if not is_admin_or_pro:
        q = q.filter(Client.user_id == current.id)
    items = paginate(q.order_by(Client.id.desc()), offset, limit)
    return items


# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create client",
    description="Create a new client. Regular users can only create for themselves. Admin/pro can create for any user.",
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Create a client with ownership/role validation."""
    role_names = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in role_names or "professional" in role_names

    # For regular users, enforce plan limits
    if not is_admin_or_pro:
        ensure_within_limits_clients(db, current)

    # For regular users, force client to be associated to themselves
    user_id = current.id if not is_admin_or_pro else getattr(payload, "user_id", None) or current.id

    obj = Client(
        user_id=user_id,
        display_name=payload.display_name,
        date_of_birth=payload.date_of_birth,
        notes=payload.notes,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.get(
    "/{client_id}",
    response_model=ClientRead,
    summary="Get client by ID",
    description="Retrieve a client by ID with ownership checks.",
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Get a client by ID with ownership/admin checks."""
    client = assert_client_ownership_or_admin(db, client_id, current)
    return client


# PUBLIC_INTERFACE
@router.put(
    "/{client_id}",
    response_model=ClientRead,
    summary="Update client",
    description="Update a client record with ownership checks.",
)
def update_client(
    client_id: int,
    payload: ClientCreate,  # reuse create schema for simplicity (display_name, dob, notes)
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Update client data with ownership checks."""
    client = assert_client_ownership_or_admin(db, client_id, current)
    client.display_name = payload.display_name
    client.date_of_birth = payload.date_of_birth
    client.notes = payload.notes
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


# PUBLIC_INTERFACE
@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete client",
    description="Delete a client with ownership checks.",
)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Delete a client with ownership checks."""
    client = assert_client_ownership_or_admin(db, client_id, current)
    db.delete(client)
    db.commit()
    return None
