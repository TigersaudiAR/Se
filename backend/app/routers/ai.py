from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user
from ..models import User
from ..services import ai, audit

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class DescriptionRequest(BaseModel):
    name_ar: str
    hints: str | None = None


class ImageRequest(BaseModel):
    prompt: str


@router.post("/description")
async def generate_description(
    payload: DescriptionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    try:
        description = await ai.generate_product_description(payload.name_ar, payload.hints)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    await audit.log_action(
        session,
        action="ai.description",
        user_id=current_user.id,
        details={"name_ar": payload.name_ar},
    )
    return {"description": description}


@router.post("/image")
async def generate_image(
    payload: ImageRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    try:
        url = await ai.generate_product_image(payload.prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    await audit.log_action(
        session,
        action="ai.image",
        user_id=current_user.id,
        details={"prompt": payload.prompt[:80]},
    )
    return {"url": url}
