from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user
from ..models import AuditLog, User
from ..schemas import AuditLogRead

router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


@router.get("", response_model=list[AuditLogRead])
async def list_logs(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    since: datetime | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[AuditLog]:
    query = select(AuditLog)
    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if since:
        query = query.where(AuditLog.created_at >= since)
    result = await session.exec(query.order_by(AuditLog.created_at.desc()))
    return result.all()
