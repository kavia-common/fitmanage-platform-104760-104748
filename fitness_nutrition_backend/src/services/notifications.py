from __future__ import annotations

from typing import Dict, Set

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionManager:
    """Manage WebSocket connections per user for real-time notifications."""

    def __init__(self) -> None:
        # Map user_id to a set of active WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    # PUBLIC_INTERFACE
    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection for a user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    # PUBLIC_INTERFACE
    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket connection for a user."""
        conns = self.active_connections.get(user_id)
        if not conns:
            return
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self.active_connections.pop(user_id, None)

    # PUBLIC_INTERFACE
    async def send_personal_message(self, user_id: int, message: dict) -> None:
        """Send a message to all active connections of a user."""
        conns = self.active_connections.get(user_id, set())
        to_remove: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                to_remove.append(ws)
            except Exception:
                # Any other exception should mark connection for cleanup
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(user_id, ws)

    # PUBLIC_INTERFACE
    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, message)


# Global singleton manager
ws_manager = ConnectionManager()
