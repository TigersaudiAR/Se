from __future__ import annotations

from typing import Any

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
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    async def broadcast(self, message: dict[str, Any]) -> None:
        for websocket in list(self.active_connections.values()):
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

    await manager.connect(user.id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            content = payload.get("message", "")
            is_command = content.startswith("/")
            chat_message = ChatMessage(
                sender_id=user.id,
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
            await manager.broadcast(
                {
                    "id": chat_message.id,
                    "sender": user.username,
                    "message": chat_message.content,
                    "is_command": is_command,
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(user.id)


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
