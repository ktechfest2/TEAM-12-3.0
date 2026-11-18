"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIMENSIONS = 768


def _ts() -> sa.Column[sa.DateTime]:
    return sa.Column(
        "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "source_passages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("document_title", sa.String(300), nullable=False),
        sa.Column("publisher", sa.String(200), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("published_on", sa.DateTime(timezone=True)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSIONS), nullable=False),
        _ts(),
    )
    op.execute(
        "CREATE INDEX ix_source_passages_embedding ON source_passages "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "claims",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("submitted_via", sa.String(32), nullable=False),
        sa.Column("screenshot_key", sa.Text()),
        _ts(),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("claim_id", sa.Uuid(), sa.ForeignKey("claims.id"), nullable=False),
        sa.Column("verdict", sa.String(32), nullable=False),
        sa.Column("passage_id", sa.Uuid(), sa.ForeignKey("source_passages.id")),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("integrity_hash", sa.String(80)),
        _ts(),
        sa.CheckConstraint(
            "verdict IN ('confirmed','contradicted','no_official_statement')",
            name="ck_messages_verdict",
        ),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("message_id", sa.Uuid(), sa.ForeignKey("messages.id"), nullable=False),
        sa.Column("reviewer_id", sa.String(120), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("note", sa.Text()),
        _ts(),
    )

    op.create_table(
        "localisations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("message_id", sa.Uuid(), sa.ForeignKey("messages.id"), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("approved_by", sa.String(120)),
        _ts(),
    )

    op.create_table(
        "deliveries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("message_id", sa.Uuid(), sa.ForeignKey("messages.id"), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("external_id", sa.String(200)),
        sa.Column("error", sa.Text()),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        _ts(),
    )
    op.create_index("ix_deliveries_message_id", "deliveries", ["message_id"])

    op.create_table(
        "subscribers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("address_hash", sa.String(80), nullable=False, unique=True),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("state", sa.String(40)),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False),
        _ts(),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("subject_id", sa.Uuid()),
        sa.Column("detail", sa.Text()),
        _ts(),
    )


def downgrade() -> None:
    for table in (
        "audit_events",
        "subscribers",
        "deliveries",
        "localisations",
        "reviews",
        "messages",
        "claims",
        "source_passages",
    ):
        op.drop_table(table)
