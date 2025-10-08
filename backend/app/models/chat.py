from __future__ import annotations

from typing import Optional

from sqlmodel import Field

from .base import TimestampedModel


class ChatMessage(TimestampedModel, table=True):
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int | None = Field(default=None, foreign_key="users.id")
    content: str
    is_command: bool = Field(default=False)
