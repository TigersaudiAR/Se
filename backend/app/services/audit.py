from __future__ import annotations

from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from ..models import AuditLog


async def log_action(
    session: AsyncSession,
    *,
    action: str,
    user_id: int | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """Persist an audit log entry."""

    entry = AuditLog(user_id=user_id, action=action, details=details or {})
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry
