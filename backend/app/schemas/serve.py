"""Pydantic schemas for model serving."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServeCreate(BaseModel):
    """Request body for POST /serve."""

    model_id: str
    gpu_type: str = "cuda"


class ServedModelRead(BaseModel):
    """Response schema for a served model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_id: str
    display_name: str
    pipeline_tag: str | None = None
    status: str
    gpu_type: str
    endpoint_url: str | None = None
    started_at: datetime
    stopped_at: datetime | None = None
    env_snippet: dict[str, str] | None = None
