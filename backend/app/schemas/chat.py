from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ChatMessageRead(BaseModel):
    id: int
    sender_id: int | None
    content: str
    is_command: bool
    created_at: datetime

    class Config:
        from_attributes = True
