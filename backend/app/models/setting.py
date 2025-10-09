from __future__ import annotations

from typing import Optional

from sqlmodel import Field

from .base import TimestampedModel


class Setting(TimestampedModel, table=True):
    __tablename__ = "settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value_encrypted: str
