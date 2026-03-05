"""ServedModel ORM model."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class ModelStatus(str, enum.Enum):
    """Status of a served model."""

    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class GPUType(str, enum.Enum):
    """GPU backend type."""

    CUDA = "cuda"
    ROCM = "rocm"


class ServedModel(Base):
    """Tracks models currently served via vLLM."""

    __tablename__ = "served_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    pipeline_tag: Mapped[str] = mapped_column(Text, nullable=True)
    endpoint_url: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus), default=ModelStatus.PENDING
    )
    gpu_type: Mapped[GPUType] = mapped_column(Enum(GPUType), nullable=False)
    container_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    stopped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
