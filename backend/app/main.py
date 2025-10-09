from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .deps import get_current_user
from .models import UserRead
from .routers import auth as auth_router
from .routers import products as products_router
from .routers import orders as orders_router

app = FastAPI(title="TwoCards Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["meta"])
def root():
    return {"name": "TwoCards", "status": "ok"}


@app.get("/healthz", tags=["meta"])
def healthz():
    return {"status": "ok"}


@app.get("/auth/me", response_model=UserRead, tags=["auth"])
def me(user: UserRead = Depends(get_current_user)):
    return user


app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(orders_router.router)
