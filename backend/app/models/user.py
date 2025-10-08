from __future__ import annotations

from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel

from .base import TimestampedModel


class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


class User(TimestampedModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: UserRole = Field(default=UserRole.ADMIN)
    theme_preference: str = Field(default="dark")


class UserCreate(SQLModel):
    username: str
    password: str
    role: UserRole = UserRole.EMPLOYEE
    theme_preference: str = "dark"


class UserRead(SQLModel):
    id: int
    username: str
    role: UserRole
    theme_preference: str


class UserUpdate(SQLModel):
    password: str | None = None
    role: UserRole | None = None
    theme_preference: str | None = None
