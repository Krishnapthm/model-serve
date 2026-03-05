"""Pydantic schemas for API keys."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class KeyCreate(BaseModel):
    """Request body for POST /keys."""

    name: str


class KeyRead(BaseModel):
    """Response schema for listing keys (no secret)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None = None
    is_active: bool


class KeyCreated(BaseModel):
    """Response schema for newly created key (shows full key once)."""

    id: uuid.UUID
    name: str
    key: str
    key_prefix: str
    created_at: datetime
