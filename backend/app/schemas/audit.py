from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None
    action: str
    details: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
