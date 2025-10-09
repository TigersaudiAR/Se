from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user
from ..models import ChatMessage, User
from ..schemas import ChatMessageRead
from ..services import audit

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self) -> None:
        self.staff_connections: dict[int, WebSocket] = {}
        self.visitor_connections: dict[str, WebSocket] = {}

    async def connect_staff(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.staff_connections[user_id] = websocket

    async def connect_visitor(self, visitor_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.visitor_connections[visitor_id] = websocket

    def disconnect_staff(self, user_id: int) -> None:
        self.staff_connections.pop(user_id, None)

    def disconnect_visitor(self, visitor_id: str) -> None:
        self.visitor_connections.pop(visitor_id, None)

    async def broadcast_to_staff(self, message: dict[str, Any]) -> None:
        for websocket in list(self.staff_connections.values()):
            await websocket.send_json(message)

    async def broadcast_to_visitors(self, message: dict[str, Any]) -> None:
        for websocket in list(self.visitor_connections.values()):
            await websocket.send_json(message)

    async def send_to_visitor(self, visitor_id: str, message: dict[str, Any]) -> None:
        websocket = self.visitor_connections.get(visitor_id)
        if websocket:
            await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
):
    token = websocket.headers.get("Authorization", "").replace("Bearer ", "")
    from ..core.security import decode_token

    try:
        username = decode_token(token)
    except Exception:
        await websocket.close()
        return
    result = await session.exec(select(User).where(User.username == username))
    user = result.one_or_none()
    if not user:
        await websocket.close()
        return

    await manager.connect_staff(user.id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            content = payload.get("message", "")
            is_command = content.startswith("/")
            chat_message = ChatMessage(
                sender_id=user.id,
                visitor_name=None,
                content=content,
                is_command=is_command,
            )
            session.add(chat_message)
            await session.commit()
            await session.refresh(chat_message)
            await audit.log_action(
                session,
                action="chat.message",
                user_id=user.id,
                details={"message_id": chat_message.id, "is_command": is_command},
            )
            payload_to_send = {
                "id": chat_message.id,
                "sender": user.username,
                "sender_type": "staff",
                "visitor_name": None,
                "message": chat_message.content,
                "is_command": is_command,
            }
            await manager.broadcast_to_staff(payload_to_send)
            await manager.broadcast_to_visitors(payload_to_send)
    except WebSocketDisconnect:
        manager.disconnect_staff(user.id)


@router.websocket("/ws/public")
async def public_websocket(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
) -> None:
    visitor_name = websocket.query_params.get("name") or "زائر"
    visitor_id = str(uuid4())
    await manager.connect_visitor(visitor_id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            content = payload.get("message", "").strip()
            if not content:
                continue
            chat_message = ChatMessage(
                sender_id=None,
                visitor_name=visitor_name,
                content=content,
                is_command=False,
            )
            session.add(chat_message)
            await session.commit()
            await session.refresh(chat_message)
            message_payload = {
                "id": chat_message.id,
                "sender": visitor_name,
                "sender_type": "visitor",
                "visitor_name": visitor_name,
                "message": chat_message.content,
                "is_command": False,
            }
            await manager.broadcast_to_staff(message_payload)
            await manager.send_to_visitor(visitor_id, message_payload)
            await audit.log_action(
                session,
                action="chat.public_message",
                user_id=None,
                details={"visitor_name": visitor_name, "message_id": chat_message.id},
            )
    except WebSocketDisconnect:
        manager.disconnect_visitor(visitor_id)


@router.get("/history", response_model=list[ChatMessageRead])
async def chat_history(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[ChatMessage]:
    result = await session.exec(
        select(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit)
    )
    messages = list(reversed(result.all()))
    return messages
