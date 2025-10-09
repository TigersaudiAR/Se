from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from .base import TimestampedModel


class Product(TimestampedModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name_ar: str
    name_en: str | None = None
    description_ar: str | None = None
    description_en: str | None = None
    sku: str | None = Field(default=None, unique=True, index=True)
    price: float = Field(default=0)
    currency: str = Field(default="SAR")
    image_url: str | None = None
    categories: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    zid_product_id: str | None = Field(default=None, index=True)
    is_active: bool = Field(default=True)
    last_synced_at: datetime | None = None
