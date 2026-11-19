"""The public record of a correction: what anyone who scans the QR code may see.

Only an approved and sealed message has a public record. Drafts, rejected and
escalated messages are never exposed. No subscriber or citizen data is included.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from clarion_api.domain.enums import ReviewStatus
from clarion_api.domain.errors import NotFoundError
from clarion_api.domain.models import Claim, Localisation, MasterMessage, SourcePassage
from clarion_api.repositories.base import AuditRepository, ClaimRepository, MessageRepository
from clarion_api.services.integrity import (
    HASH_ALGORITHM,
    NO_PREVIOUS_HASH,
    canonical_json,
    verify,
)
from clarion_api.services.messages import SEALED_ACTION


@dataclass(frozen=True)
class PublicRecord:
    message: MasterMessage
    claim: Claim
    source: SourcePassage | None
    translations: tuple[Localisation, ...]
    approved_by: str
    approved_at: datetime
    sealed_at: datetime
    integrity_hash: str
    previous_hash: str | None
    canonical_json: str
    integrity_verified: bool
    hash_algorithm: str = HASH_ALGORITHM


async def load_public_record(
    message_id: UUID,
    *,
    messages: MessageRepository,
    claims: ClaimRepository,
    audit: AuditRepository,
) -> PublicRecord:
    """Build the record, or raise NotFoundError for anything that is not approved and sealed."""
    message = await messages.get(message_id)
    review = message.review if message else None
    if (
        message is None
        or review is None
        or review.status is not ReviewStatus.APPROVED
        or message.integrity_hash is None
    ):
        msg = "no published correction with this id"
        raise NotFoundError(msg)
    claim = await claims.get(message.claim_id)
    events = await audit.list_for_subject(message.id, action=SEALED_ACTION)
    if claim is None or not events:
        msg = "no published correction with this id"
        raise NotFoundError(msg)
    sealing = events[-1]
    previous = None if sealing.detail in (None, NO_PREVIOUS_HASH) else sealing.detail
    return PublicRecord(
        message=message,
        claim=claim,
        source=message.passage,
        translations=tuple(loc for loc in message.localisations if loc.is_approved),
        approved_by=review.reviewer_id,
        approved_at=review.created_at,
        sealed_at=sealing.created_at,
        integrity_hash=message.integrity_hash,
        previous_hash=previous,
        canonical_json=canonical_json(message, previous),
        integrity_verified=verify(message, previous),
    )
