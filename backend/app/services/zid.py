from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import settings
from ..models import Product
from . import audit

ZID_BASE_URL = "https://api.zid.store/v1"


class ZidError(RuntimeError):
    pass


def to_zid_product_payload(product: Product) -> dict[str, Any]:
    """Transform an internal product into the Zid API structure."""

    return {
        "name": product.name_ar,
        "description": product.description_ar or "",
        "price": product.price,
        "sku": product.sku,
        "is_active": product.is_active,
        "images": [product.image_url] if product.image_url else [],
        "metadata": {
            "name_en": product.name_en,
            "description_en": product.description_en,
            "categories": product.categories or [],
        },
    }


def _auth_headers() -> dict[str, str]:
    if not settings.zid_token:
        raise ZidError("ZID token is not configured")
    return {"Authorization": f"Bearer {settings.zid_token}"}


async def _request(method: str, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method,
            f"{ZID_BASE_URL}{endpoint}",
            json=payload,
            headers=_auth_headers(),
        )
        data = response.json()
        if response.status_code >= 400:
            raise ZidError(data)
        return data


async def create_product(session: AsyncSession, product: Product) -> str | None:
    try:
        data = await _request("POST", "/products", to_zid_product_payload(product))
        zid_id = data.get("data", {}).get("id") or data.get("id")
        await audit.log_action(
            session,
            action="zid.create_product",
            details={"payload": to_zid_product_payload(product), "response": data},
        )
        return str(zid_id) if zid_id else None
    except Exception as exc:
        await audit.log_action(
            session,
            action="zid.create_product.error",
            details={"error": str(exc)},
        )
        return None


async def update_product(session: AsyncSession, product: Product) -> bool:
    if not product.zid_product_id:
        raise ZidError("Product has not been pushed to Zid yet")
    try:
        data = await _request(
            "PUT", f"/products/{product.zid_product_id}", to_zid_product_payload(product)
        )
        product.last_synced_at = datetime.utcnow()
        await session.commit()
        await audit.log_action(
            session,
            action="zid.update_product",
            details={"product_id": product.id, "response": data},
        )
        return True
    except Exception as exc:
        await audit.log_action(
            session,
            action="zid.update_product.error",
            details={"product_id": product.id, "error": str(exc)},
        )
        return False


async def import_vouchers(
    session: AsyncSession, *, product: Product, codes: list[str]
) -> bool:
    try:
        payload = {"product_id": product.zid_product_id, "codes": codes}
        data = await _request("POST", "/vouchers/import", payload)
        await audit.log_action(
            session,
            action="zid.import_vouchers",
            details={"product_id": product.id, "response": data},
        )
        return True
    except Exception as exc:
        await audit.log_action(
            session,
            action="zid.import_vouchers.error",
            details={"product_id": product.id, "error": str(exc)},
        )
        return False
