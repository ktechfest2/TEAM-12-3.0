"""Database tables. Naming: plural snake_case tables, singular snake_case columns,
foreign keys as <entity>_id, timestamps as <verb>_at in UTC."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, MetaData, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIMENSIONS = 768

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourcePassageRow(Timestamped, Base):
    __tablename__ = "source_passages"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    document_title: Mapped[str] = mapped_column(String(300))
    publisher: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(Text)
    published_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))


class ClaimRow(Timestamped, Base):
    __tablename__ = "claims"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8))
    submitted_via: Mapped[str] = mapped_column(String(32))
    screenshot_key: Mapped[str | None] = mapped_column(Text)


class MessageRow(Timestamped, Base):
    __tablename__ = "messages"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    claim_id: Mapped[UUID] = mapped_column(ForeignKey("claims.id"))
    verdict: Mapped[str] = mapped_column(String(32))
    passage_id: Mapped[UUID | None] = mapped_column(ForeignKey("source_passages.id"))
    summary: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    integrity_hash: Mapped[str | None] = mapped_column(String(80))


class ReviewRow(Timestamped, Base):
    __tablename__ = "reviews"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"))
    reviewer_id: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(16))
    note: Mapped[str | None] = mapped_column(Text)


class LocalisationRow(Timestamped, Base):
    __tablename__ = "localisations"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"))
    language: Mapped[str] = mapped_column(String(8))
    text: Mapped[str] = mapped_column(Text)
    approved_by: Mapped[str | None] = mapped_column(String(120))


class DeliveryRow(Timestamped, Base):
    __tablename__ = "deliveries"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"))
    channel: Mapped[str] = mapped_column(String(32))
    language: Mapped[str] = mapped_column(String(8))
    status: Mapped[str] = mapped_column(String(16))
    external_id: Mapped[str | None] = mapped_column(String(200))
    error: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SubscriberRow(Timestamped, Base):
    __tablename__ = "subscribers"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    channel: Mapped[str] = mapped_column(String(32))
    address_hash: Mapped[str] = mapped_column(String(80), unique=True)
    language: Mapped[str] = mapped_column(String(8))
    state: Mapped[str | None] = mapped_column(String(40))
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SmsSubscriptionRow(Timestamped, Base):
    """Phone subscribers. The number is encrypted; the hash finds it. Everything else
    (preferences, code state, send counters) lives in `payload`."""

    __tablename__ = "sms_subscriptions"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    phone_hash: Mapped[str] = mapped_column(String(80), unique=True)
    phone_encrypted: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)


class AuditEventRow(Timestamped, Base):
    __tablename__ = "audit_events"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(64))
    subject_id: Mapped[UUID | None]
    detail: Mapped[str | None] = mapped_column(Text)
