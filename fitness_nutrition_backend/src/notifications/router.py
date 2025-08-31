from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.api.utils import pagination_params, paginate
from src.core.database import get_db
from src.core.security import get_current_user
from src.models import Notification, User
from src.schemas.notification import NotificationRead
from src.schemas.notifications_requests import NotificationCreate
from src.services.notifications import ws_manager

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=list[NotificationRead],
    summary="List notifications",
    description="List notifications for the current user with pagination.",
)
def list_notifications(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    offset_limit: tuple[int, int] = Depends(pagination_params),
    is_read: Optional[bool] = Query(default=None, description="Filter by read status"),
):
    """Return notifications belonging to the current user with optional is_read filtering."""
    offset, limit = offset_limit
    q = db.query(Notification).filter(Notification.user_id == current.id)
    if is_read is not None:
        q = q.filter(Notification.is_read == is_read)
    items = paginate(q.order_by(Notification.id.desc()), offset, limit)
    return items





# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=NotificationRead,
    summary="Create notification",
    description="Create a notification for yourself. Admin/pro can target other users in future revisions.",
)
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Create a notification for current user and push via WebSocket if connected."""
    target_user_id = current.id
    obj = Notification(user_id=target_user_id, title=payload.title, message=payload.message, is_read=False)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    # Push real-time
    import anyio
    async def _push():
        await ws_manager.send_personal_message(target_user_id, {"type": "notification", "payload": NotificationRead.model_validate(obj).model_dump()})
    try:
        anyio.run(_push)
    except Exception:
        # Best-effort push; ignore failures
        pass
    return obj


# PUBLIC_INTERFACE
@router.post(
    "/{notification_id}/read",
    response_model=NotificationRead,
    summary="Mark notification as read",
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Mark a user's notification as read."""
    obj = db.get(Notification, notification_id)
    if not obj or obj.user_id != current.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    obj.is_read = True
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
@router.delete(
    "/{notification_id}",
    summary="Delete notification",
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Delete a user's notification."""
    obj = db.get(Notification, notification_id)
    if not obj or obj.user_id != current.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted"}


# PUBLIC_INTERFACE
@router.websocket(
    "/ws",
)
async def notifications_ws(websocket: WebSocket):
    """WebSocket endpoint for receiving real-time notifications.

    Usage:
    - Connect with /api/notifications/ws?token=<JWT>
    - On connect, the server validates the token and registers the connection by user.
    - Server pushes events as {"type":"notification","payload":{...}}.
    """
    # Extract token from query string for authentication
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    # Validate token and resolve user
    from src.core.security import decode_token
    from src.core.database import SessionLocal
    claims = None
    try:
        claims = decode_token(token)
    except Exception:
        await websocket.close(code=4401)
        return
    sub = claims.get("sub")
    if not sub:
        await websocket.close(code=4401)
        return
    user_id = int(sub)

    # Optionally verify user exists/active
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user or not user.is_active:
            await websocket.close(code=4401)
            return
    finally:
        db.close()

    await ws_manager.connect(user_id, websocket)
    try:
        # Keep the connection open; echo pings or simple acks
        while True:
            msg = await websocket.receive_text()
            # Minimal protocol: client can send "ping" to keepalive
            if msg.strip().lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
    except Exception:
        ws_manager.disconnect(user_id, websocket)
