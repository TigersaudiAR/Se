from __future__ import annotations

from typing import Any

import httpx

from ..core.config import settings

WHATSAPP_API_URL = "https://graph.facebook.com/v19.0"


class WhatsAppError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    if not settings.whatsapp_token:
        raise WhatsAppError("WhatsApp token is not configured")
    return {"Authorization": f"Bearer {settings.whatsapp_token}", "Content-Type": "application/json"}


async def send_template(
    *,
    to: str,
    template_name: str,
    language_code: str = "ar",
    components: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not settings.whatsapp_phone_id:
        raise WhatsAppError("WhatsApp phone ID is not configured")
    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }
    if components:
        payload["template"]["components"] = components
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_id}/messages",
            json=payload,
            headers=_headers(),
        )
        data = response.json()
        if response.status_code >= 400:
            raise WhatsAppError(data)
        return data
