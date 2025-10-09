from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = Field(default="TwoCards Platform")
    secret_key: str = Field(default="change-this-secret")
    access_token_expire_minutes: int = Field(default=60 * 12)
    jwt_algorithm: str = Field(default="HS256")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./twocards.db",
        validation_alias="DATABASE_URL",
    )

    zid_token: str | None = Field(default=None, validation_alias="ZID_TOKEN")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    whatsapp_token: str | None = Field(default=None, validation_alias="WA_TOKEN")
    whatsapp_phone_id: str | None = Field(default=None, validation_alias="WA_PHONE_ID")
    email_tokens: str | None = Field(default=None, validation_alias="EMAIL_TOKENS")

    encryption_secret: str = Field(
        default="twocards-encryption-key-please-change",
        validation_alias="ENCRYPTION_SECRET",
    )

    cors_allow_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def model_post_init(self, __context: Any) -> None:  # pragma: no cover - settings hook
        if not self.secret_key or self.secret_key == "change-this-secret":
            # The developer should change this, but we keep a functional default for local dev.
            self.secret_key = "development-secret-key"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
