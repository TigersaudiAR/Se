from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user
from ..models import User
from ..services import audit
from ..services.integration_checks import collect_status

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status")
async def system_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    statuses = await collect_status()
    await audit.log_action(
        session,
        action="system.status_checked",
        user_id=current_user.id,
        details={"checks": [status["name"] for status in statuses]},
    )
    return {"services": statuses}
