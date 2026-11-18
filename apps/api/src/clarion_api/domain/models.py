"""Domain entities as immutable pydantic models.

These are the shapes services pass around. Database rows live in clarion_api.db
and are mapped to these in repositories.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from clarion_api.domain.enums import (
    ChannelKind,
    DeliveryStatus,
    Language,
    RenditionFormat,
    ReviewStatus,
    Verdict,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class Entity(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)


class SourcePassage(Entity):
    """A quotable passage from an official document (INEC statement, Electoral Act)."""

    document_title: str
    publisher: str
    url: HttpUrl
    published_on: datetime | None = None
    text: str


class Claim(Entity):
    text: str
    language: Language = Language.ENGLISH
    submitted_via: ChannelKind = ChannelKind.WEB_FEED
    screenshot_key: str | None = None


class VerdictResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    verdict: Verdict
    passage_id: UUID | None
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


class Review(Entity):
    claim_id: UUID
    reviewer_id: str
    status: ReviewStatus
    note: str | None = None


class Localisation(Entity):
    language: Language
    text: str
    approved_by: str | None = None

    @property
    def is_approved(self) -> bool:
        return self.approved_by is not None


class MasterMessage(Entity):
    """The single approved answer every rendition is derived from."""

    claim_id: UUID
    verdict: Verdict
    passage: SourcePassage | None
    summary: str
    review: Review | None = None
    localisations: tuple[Localisation, ...] = ()
    integrity_hash: str | None = None


class Rendition(Entity):
    message_id: UUID
    language: Language
    format: RenditionFormat
    text: str | None = None
    media_key: str | None = None


class Delivery(Entity):
    message_id: UUID
    channel: ChannelKind
    language: Language
    status: DeliveryStatus = DeliveryStatus.QUEUED
    external_id: str | None = None
    error: str | None = None
