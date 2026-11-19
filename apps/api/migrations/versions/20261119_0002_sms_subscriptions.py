"""sms subscriptions

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sms_subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("phone_hash", sa.String(80), nullable=False),
        sa.Column("phone_encrypted", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sms_subscriptions")),
        sa.UniqueConstraint("phone_hash", name=op.f("uq_sms_subscriptions_phone_hash")),
    )
    op.create_index("ix_sms_subscriptions_status", "sms_subscriptions", ["status"])


def downgrade() -> None:
    op.drop_index("ix_sms_subscriptions_status", table_name="sms_subscriptions")
    op.drop_table("sms_subscriptions")
