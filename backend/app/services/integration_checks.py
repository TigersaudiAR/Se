from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import httpx

from ..core.config import settings


class IntegrationStatus:
    def __init__(self, name: str, configured: bool, ok: bool, message: str) -> None:
        self.name = name
        self.configured = configured
        self.ok = ok
        self.message = message
        self.checked_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "configured": self.configured,
            "ok": self.ok,
            "message": self.message,
            "checked_at": self.checked_at.isoformat() + "Z",
        }


async def _http_check(url: str, headers: dict[str, str] | None = None) -> tuple[bool, str]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
        if response.status_code < 400:
            return True, "نجح الاتصال التجريبي"
        return False, f"خطأ HTTP {response.status_code}: {response.text[:120]}"
    except Exception as exc:  # pragma: no cover - defensive guard
        return False, f"تعذر إجراء الاتصال: {exc}"


async def check_zid() -> IntegrationStatus:
    token = settings.zid_token
    if not token:
        return IntegrationStatus("zid", False, False, "لم يتم ضبط مفتاح زد بعد")
    ok, message = await _http_check(
        "https://api.zid.sa/v1/products",
        headers={"Authorization": f"Bearer {token}"},
    )
    return IntegrationStatus("zid", True, ok, message)


async def check_openai() -> IntegrationStatus:
    token = settings.openai_api_key
    if not token:
        return IntegrationStatus("openai", False, False, "مفتاح OpenAI غير متوفر")
    ok, message = await _http_check(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {token}"},
    )
    return IntegrationStatus("openai", True, ok, message)


async def check_whatsapp() -> IntegrationStatus:
    token = settings.wa_token
    phone_id = settings.wa_phone_id
    if not token or not phone_id:
        return IntegrationStatus(
            "whatsapp",
            False,
            False,
            "بيانات واتساب ناقصة (الرمز أو معرف الرقم)",
        )
    url = f"https://graph.facebook.com/v17.0/{phone_id}/message_templates"
    ok, message = await _http_check(url, headers={"Authorization": f"Bearer {token}"})
    return IntegrationStatus("whatsapp", True, ok, message)


async def check_email() -> IntegrationStatus:
    if not settings.email_tokens:
        return IntegrationStatus("email", False, False, "لا توجد حسابات بريد متصلة بعد")
    # Currently OAuth validation requires interactive consent; confirm storage only.
    return IntegrationStatus(
        "email",
        True,
        True,
        "تم العثور على رموز بريد إلكتروني مخزنة وجاهزة للاستخدام",
    )


async def collect_status() -> list[dict[str, Any]]:
    results = await asyncio.gather(
        check_zid(),
        check_openai(),
        check_whatsapp(),
        check_email(),
    )
    return [status.to_dict() for status in results]
