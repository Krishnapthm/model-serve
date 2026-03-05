"""Pydantic schemas for HuggingFace models."""

from pydantic import BaseModel, ConfigDict


class ModelSummary(BaseModel):
    """Summary of a HuggingFace model for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    pipeline_tag: str | None = None
    description: str | None = None
    downloads: int = 0
    likes: int = 0
    label: str = ""
    badge_color: str = "gray"


class ModelDetail(BaseModel):
    """Detailed view of a single HuggingFace model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    pipeline_tag: str | None = None
    description: str | None = None
    downloads: int = 0
    likes: int = 0
    label: str = ""
    badge_color: str = "gray"
    model_card_url: str = ""
    library_name: str | None = None
    tags: list[str] = []
