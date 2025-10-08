from __future__ import annotations

from typing import Any

import httpx

from ..core.config import settings

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"


class AIServiceError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    if not settings.openai_api_key:
        raise AIServiceError("OpenAI API key is not configured")
    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }


async def generate_product_description(name_ar: str, hints: str | None = None) -> str:
    payload: dict[str, Any] = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "أنت مساعد خبير في كتابة وصف المنتجات الرقمية باللهجة العربية الرسمية.",
            },
            {
                "role": "user",
                "content": f"اكتب وصفًا تسويقيًا قصيرًا للمنتج: {name_ar}. {hints or ''}",
            },
        ],
    }
    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(OPENAI_CHAT_URL, json=payload, headers=_headers())
        data = response.json()
        if response.status_code >= 400:
            raise AIServiceError(data)
        message = data["choices"][0]["message"]["content"].strip()
        return message


async def generate_product_image(prompt: str) -> str:
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OPENAI_IMAGE_URL, json=payload, headers=_headers())
        data = response.json()
        if response.status_code >= 400:
            raise AIServiceError(data)
        return data["data"][0]["url"]
