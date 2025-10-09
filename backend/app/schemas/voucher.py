from __future__ import annotations

from datetime import datetime
from typing import Iterable

from pydantic import BaseModel


class VoucherImport(BaseModel):
    product_id: int
    codes: Iterable[str]
    also_push_to_zid: bool = False
    notes: str | None = None


class VoucherRead(BaseModel):
    id: int
    product_id: int
    code: str
    is_redeemed: bool
    redeemed_at: datetime | None

    class Config:
        from_attributes = True
