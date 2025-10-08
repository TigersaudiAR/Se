from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field

from .base import TimestampedModel


class AuditLog(TimestampedModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id")
    action: str
    details: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
