from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .base import TimestampedModel


class Voucher(TimestampedModel, table=True):
    __tablename__ = "vouchers"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    code: str = Field(index=True, unique=True)
    is_redeemed: bool = Field(default=False)
    redeemed_at: datetime | None = None
    notes: str | None = None
