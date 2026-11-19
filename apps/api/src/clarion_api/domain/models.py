"""Domain entities as immutable pydantic models.

These are the shapes services pass around. Database rows live in clarion_api.db
and are mapped to these in repositories.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from clarion_api.domain.enums import (
    ChannelKind,
    DeliveryMode,
    DeliveryStatus,
    DigestFrequency,
    Language,
    RenditionFormat,
    ReviewStatus,
    SubscriptionStatus,
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
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
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
    sent_at: datetime | None = None


class Subscriber(Entity):
    """Someone who asked for future corrections. The address is stored only as a hash."""

    channel: ChannelKind
    address_hash: str
    language: Language
    state: str | None = None
    consented_at: datetime = Field(default_factory=utc_now)


class SmsPreferences(BaseModel):
    """What a person asked to receive. Validated again server side; the form is not trusted."""

    model_config = ConfigDict(frozen=True)

    languages: list[Language] = Field(min_length=1, max_length=5)
    mode: DeliveryMode = DeliveryMode.INSTANT
    digest_frequency: DigestFrequency = DigestFrequency.DAILY
    max_per_day: int = Field(default=3, ge=1, le=10)


class SmsSubscription(Entity):
    """A phone number that asked for corrections by SMS.

    The number is stored encrypted; `phone_hash` finds it again. It stays `pending`
    until the owner types the code we texted, and `consented_at` is set only then.
    Requested changes (new preferences, or removal) wait in `requested` until a code
    confirms them, so typing someone else's number changes nothing.
    """

    phone_hash: str
    phone_encrypted: str
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    preferences: SmsPreferences
    requested: SmsPreferences | None = None
    unsubscribe_requested: bool = False
    consented_at: datetime | None = None
    code_hash: str | None = None
    code_sent_at: datetime | None = None
    code_expires_at: datetime | None = None
    code_attempts: int = 0
    # Daily cap bookkeeping. `sent_on` is the local (Lagos) date the counter belongs to.
    sent_on: str | None = None
    sent_today: int = 0
    last_sent_at: datetime | None = None
    held_message_ids: list[UUID] = Field(default_factory=list)
    seen_message_ids: list[UUID] = Field(default_factory=list)


class AuditEvent(Entity):
    """Who did what to which record. Never holds message bodies or personal data."""

    actor: str
    action: str
    subject_id: UUID | None = None
    detail: str | None = None
