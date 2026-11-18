"""Integrity seal for approved messages.

The hash covers the claim, verdict, cited source, summary, approver and every
approved translation, serialised canonically. Anyone holding the public record
can recompute it; a changed word gives a different hash.
"""

import hashlib
import json
from typing import Any

from clarion_api.domain.models import MasterMessage

HASH_ALGORITHM = "sha256"


def canonical_payload(message: MasterMessage, previous_hash: str | None) -> dict[str, Any]:
    return {
        "message_id": str(message.id),
        "claim_id": str(message.claim_id),
        "verdict": message.verdict.value,
        "source_url": str(message.passage.url) if message.passage else None,
        "source_text": message.passage.text if message.passage else None,
        "summary": message.summary,
        "approved_by": message.review.reviewer_id if message.review else None,
        "localisations": sorted(
            (loc.language.value, loc.text, loc.approved_by or "")
            for loc in message.localisations
            if loc.is_approved
        ),
        "previous_hash": previous_hash,
    }


def compute_hash(message: MasterMessage, previous_hash: str | None = None) -> str:
    payload = canonical_payload(message, previous_hash)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.new(HASH_ALGORITHM, encoded.encode("utf-8")).hexdigest()
    return f"{HASH_ALGORITHM}:{digest}"


def seal(message: MasterMessage, previous_hash: str | None = None) -> MasterMessage:
    return message.model_copy(update={"integrity_hash": compute_hash(message, previous_hash)})


def verify(message: MasterMessage, previous_hash: str | None = None) -> bool:
    return message.integrity_hash == compute_hash(message, previous_hash)
