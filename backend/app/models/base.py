from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class TimestampedModel(SQLModel):
    """Mixin that adds created/updated timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = ["TimestampedModel"]
