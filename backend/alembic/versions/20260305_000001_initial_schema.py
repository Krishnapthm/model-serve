"""Create initial schema with users, api_keys, and served_models.

Revision ID: 20260305_000001
Revises:
Create Date: 2026-03-05 00:00:01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260305_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply schema changes."""
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
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("key_hash", sa.Text(), nullable=False),
        sa.Column("key_prefix", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_api_keys_owner_id"), "api_keys", ["owner_id"], unique=False
    )

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


def downgrade() -> None:
    """Revert schema changes."""
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

    op.drop_index(op.f("ix_served_models_owner_id"), table_name="served_models")
    op.drop_table("served_models")
    op.drop_index(op.f("ix_api_keys_owner_id"), table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    gpu_type.drop(op.get_bind(), checkfirst=True)
    model_status.drop(op.get_bind(), checkfirst=True)
