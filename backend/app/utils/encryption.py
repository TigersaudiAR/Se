from __future__ import annotations

import base64
from typing import Final

from cryptography.fernet import Fernet, InvalidToken

from ..core.config import settings


def _get_fernet() -> Fernet:
    key_material = settings.encryption_secret.encode("utf-8")
    key = base64.urlsafe_b64encode(key_material[:32].ljust(32, b"0"))
    return Fernet(key)


FERNET: Final[Fernet] = _get_fernet()


def encrypt_value(value: str) -> str:
    return FERNET.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(value_encrypted: str) -> str:
    try:
        return FERNET.decrypt(value_encrypted.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:  # pragma: no cover - indicates data tampering
        raise ValueError("Unable to decrypt value") from exc
