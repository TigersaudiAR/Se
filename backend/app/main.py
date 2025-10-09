from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from .core.config import settings
from .core.security import get_password_hash
from .db.session import get_session, init_db
from .models import User, UserRole
from .routers import (
    ai,
    auth,
    chat,
    logs,
    products,
    settings as settings_router,
    system,
    users,
    vouchers,
    whatsapp,
)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    async with get_session() as session:
        result = await session.exec(select(User).where(User.username == "admin"))
        admin = result.one_or_none()
        if not admin:
            user = User(
                username="admin",
                password_hash=get_password_hash("Admin@123"),
                role=UserRole.ADMIN,
            )
            session.add(user)
            await session.commit()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(vouchers.router)
app.include_router(logs.router)
app.include_router(settings_router.router)
app.include_router(ai.router)
app.include_router(whatsapp.router)
app.include_router(chat.router)
app.include_router(system.router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
