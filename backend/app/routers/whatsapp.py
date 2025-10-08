from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user
from ..models import User
from ..services import audit, whatsapp

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])


class WhatsAppRequest(BaseModel):
    to: str
    template_name: str
    language_code: str = "ar"
    variables: dict[str, str] | None = None


@router.post("/send")
async def send_template(
    payload: WhatsAppRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    components = []
    if payload.variables:
        components.append(
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": value}
                    for value in payload.variables.values()
                ],
            }
        )
    try:
        response = await whatsapp.send_template(
            to=payload.to,
            template_name=payload.template_name,
            language_code=payload.language_code,
            components=components or None,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    await audit.log_action(
        session,
        action="whatsapp.send",
        user_id=current_user.id,
        details={"to": payload.to, "template": payload.template_name},
    )
    return {"status": "sent", "id": response.get("messages", [{}])[0].get("id", "-")}
