from __future__ import annotations

from typing import Any

from ..core.config import settings
from ..utils.encryption import decrypt_value


def list_connected_accounts() -> list[dict[str, Any]]:
    if not settings.email_tokens:
        return []
    accounts: list[dict[str, Any]] = []
    for entry in settings.email_tokens.split(","):
        if not entry:
            continue
        try:
            decoded = decrypt_value(entry)
            provider, email = decoded.split(":", maxsplit=1)
            accounts.append({"provider": provider, "email": email})
        except Exception:  # pragma: no cover - defensive
            continue
    return accounts


def iframe_for_provider(provider: str) -> str:
    provider = provider.lower()
    if provider == "gmail":
        return "https://mail.google.com"
    if provider == "outlook":
        return "https://outlook.office.com/mail/"
    raise ValueError("Unsupported provider")
