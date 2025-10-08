from __future__ import annotations

from pydantic import BaseModel


class SettingItem(BaseModel):
    key: str
    value: str | None = None


class SettingsPayload(BaseModel):
    values: list[SettingItem]
