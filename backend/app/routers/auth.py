from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.security import create_access_token, verify_password
from ..db.session import get_session
from ..dependencies.auth import get_current_user
from ..models import User
from ..schemas import Token
from ..services import audit

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> Token:
    result = await session.exec(select(User).where(User.username == payload.username))
    user = result.one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="بيانات الدخول غير صحيحة")
    token = create_access_token(subject=user.username, expires_delta=timedelta(minutes=60 * 12))
    await audit.log_action(
        session,
        action="auth.login",
        user_id=user.id,
        details={"username": user.username},
    )
    return Token(access_token=token)


@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {
        "username": current_user.username,
        "role": current_user.role,
        "theme_preference": current_user.theme_preference,
    }
