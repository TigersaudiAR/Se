from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_admin
from ..models import Setting, User
from ..schemas import SettingItem, SettingsPayload
from ..services import audit
from ..utils.encryption import decrypt_value, encrypt_value

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

SECRET_KEYS = [
    "ZID_TOKEN",
    "OPENAI_API_KEY",
    "WA_TOKEN",
    "WA_PHONE_ID",
    "EMAIL_TOKENS",
]


@router.get("", response_model=list[SettingItem])
async def read_settings(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin),
) -> list[SettingItem]:
    result = await session.exec(select(Setting).where(Setting.key.in_(SECRET_KEYS)))
    settings_rows = result.all()
    items: list[SettingItem] = []
    for row in settings_rows:
        try:
            value = decrypt_value(row.value_encrypted)
        except Exception:
            value = None
        items.append(SettingItem(key=row.key, value=value))
    await audit.log_action(
        session,
        action="settings.read",
        user_id=current_user.id,
        details={"count": len(items)},
    )
    return items


@router.post("")
async def update_settings(
    payload: SettingsPayload,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin),
) -> dict[str, int]:
    updated = 0
    for item in payload.values:
        encrypted = encrypt_value(item.value or "")
        result = await session.exec(select(Setting).where(Setting.key == item.key))
        existing = result.one_or_none()
        if existing:
            existing.value_encrypted = encrypted
            updated += 1
        else:
            session.add(Setting(key=item.key, value_encrypted=encrypted))
            updated += 1
    await session.commit()
    await audit.log_action(
        session,
        action="settings.update",
        user_id=current_user.id,
        details={"updated": updated},
    )
    return {"updated": updated}
