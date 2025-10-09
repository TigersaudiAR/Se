from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.security import get_password_hash
from ..db.session import get_session
from ..dependencies.auth import get_current_admin
from ..models import User, UserCreate, UserRead, UserUpdate
from ..services import audit

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> list[User]:
    result = await session.exec(select(User))
    return result.all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> User:
    exists = await session.exec(select(User).where(User.username == payload.username))
    if exists.one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="المستخدم موجود مسبقًا")
    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        theme_preference=payload.theme_preference,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await audit.log_action(
        session,
        action="users.create",
        user_id=current_admin.id,
        details={"user_id": user.id, "username": user.username},
    )
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> User:
    result = await session.exec(select(User).where(User.id == user_id))
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المستخدم غير موجود")
    if payload.password:
        user.password_hash = get_password_hash(payload.password)
    if payload.role:
        user.role = payload.role
    if payload.theme_preference:
        user.theme_preference = payload.theme_preference
    await session.commit()
    await session.refresh(user)
    await audit.log_action(
        session,
        action="users.update",
        user_id=current_admin.id,
        details={"user_id": user.id},
    )
    return user
