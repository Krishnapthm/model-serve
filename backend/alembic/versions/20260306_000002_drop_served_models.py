"""Drop served_models table and gpu_type/model_status enums.

Revision ID: 20260306_000002
Revises: 20260305_000001
Create Date: 2026-03-06 00:00:01
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260306_000002"
down_revision: Union[str, None] = "20260305_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop served_models table and associated enums."""
    op.drop_index(op.f("ix_served_models_owner_id"), table_name="served_models")
    op.drop_table("served_models")

    model_status = postgresql.ENUM(
        "pending",
        "running",
        "stopped",
        "error",
        name="modelstatus",
        create_type=False,
    )
    gpu_type = postgresql.ENUM(
        "cuda",
        "rocm",
        name="gputype",
        create_type=False,
    )
    model_status.drop(op.get_bind(), checkfirst=True)
    gpu_type.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Recreate served_models table and enums."""
    import sqlalchemy as sa

    model_status = postgresql.ENUM(
        "pending",
        "running",
        "stopped",
        "error",
        name="modelstatus",
        create_type=False,
    )
    gpu_type = postgresql.ENUM(
        "cuda",
        "rocm",
        name="gputype",
        create_type=False,
    )
    model_status.create(op.get_bind(), checkfirst=True)
    gpu_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "served_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("pipeline_tag", sa.Text(), nullable=True),
        sa.Column("endpoint_url", sa.Text(), nullable=True),
        sa.Column("status", model_status, nullable=False),
        sa.Column("gpu_type", gpu_type, nullable=False),
        sa.Column("container_id", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_served_models_owner_id"), "served_models", ["owner_id"], unique=False
    )
