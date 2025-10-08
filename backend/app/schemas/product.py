from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name_ar: str
    name_en: str | None = None
    description_ar: str | None = None
    description_en: str | None = None
    sku: str | None = Field(default=None, max_length=64)
    price: float = 0
    currency: str = "SAR"
    image_url: str | None = None
    categories: list[str] | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    zid_product_id: str | None = None


class ProductUpdate(ProductBase):
    zid_product_id: str | None = None


class ProductRead(ProductBase):
    id: int
    zid_product_id: str | None = None
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
