"""Pydantic schemas for served model info."""

from pydantic import BaseModel


class ServedModelRead(BaseModel):
    """Response schema for a configured vLLM model slot."""

    slot: int
    model_id: str
    display_name: str
    endpoint_url: str
    status: str
    env_snippet: dict[str, str]
