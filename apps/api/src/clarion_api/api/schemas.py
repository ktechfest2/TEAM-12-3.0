"""Public request and response shapes. Changing these changes contracts/openapi.json."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from clarion_api.domain.enums import Language, Verdict
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
