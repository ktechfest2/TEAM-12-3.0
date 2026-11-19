"""Public request and response shapes. Changing these changes contracts/openapi.json."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from clarion_api.domain.enums import ChannelKind, DeliveryStatus, Language, ReviewStatus, Verdict
from clarion_api.services.rendering.sms import SmsEncoding


class HealthOut(BaseModel):
    status: str
    version: str
    env: str


class ClaimIn(BaseModel):
    text: str = Field(min_length=3, max_length=4000)
    language: Language = Language.ENGLISH


class SourceOut(BaseModel):
    id: UUID
    document_title: str
    publisher: str
    url: str
    text: str


class ClaimOut(BaseModel):
    id: UUID
    text: str
    language: Language
    created_at: datetime
    verdict: Verdict
    rationale: str
    confidence: float
    source: SourceOut | None


class SmsSizeIn(BaseModel):
    text: str = Field(max_length=2000)


class SmsSizeOut(BaseModel):
    encoding: SmsEncoding
    units: int
    segments: int
    per_segment_limit: int


class MessageCreateIn(BaseModel):
    claim_id: UUID


class ReviewIn(BaseModel):
    status: ReviewStatus
    note: str | None = Field(default=None, max_length=2000)
    summary: str | None = Field(default=None, min_length=3, max_length=1000)


class ReviewOut(BaseModel):
    reviewer_id: str
    status: ReviewStatus
    note: str | None
    created_at: datetime


class LocalisationIn(BaseModel):
    language: Language
    text: str | None = Field(default=None, min_length=1, max_length=1000)


class LocalisationOut(BaseModel):
    language: Language
    text: str
    approved_by: str | None
    is_approved: bool


class MessageOut(BaseModel):
    id: UUID
    claim_id: UUID
    verdict: Verdict
    summary: str
    confidence: float
    source: SourceOut | None
    review: ReviewOut | None
    localisations: list[LocalisationOut]
    integrity_hash: str | None
    created_at: datetime


class BroadcastIn(BaseModel):
    languages: list[Language] | None = None


class RetractIn(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class DeliveryOut(BaseModel):
    id: UUID
    message_id: UUID
    channel: ChannelKind
    language: Language
    status: DeliveryStatus
    external_id: str | None
    error: str | None
    sent_at: datetime | None
    created_at: datetime


class TokenIn(BaseModel):
    invite_code: str = Field(min_length=1, max_length=200)
    reviewer_name: str = Field(min_length=1, max_length=120)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 - the OAuth token type name, not a secret
    expires_in_seconds: int
    reviewer_name: str
