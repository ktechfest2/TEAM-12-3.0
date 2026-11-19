from uuid import UUID

from fastapi import APIRouter

from clarion_api.api.deps import ContainerDep
from clarion_api.api.mappers import source_out
from clarion_api.api.schemas import PublicCorrectionOut, PublicTranslationOut
from clarion_api.services.public_record import load_public_record

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/corrections/{message_id}", operation_id="getPublicCorrection")
async def get_public_correction(message_id: UUID, container: ContainerDep) -> PublicCorrectionOut:
    """No sign in. Only approved and sealed corrections exist here; anything else is a 404."""
    record = await load_public_record(
        message_id,
        messages=container.messages,
        claims=container.claims,
        audit=container.audit,
    )
    return PublicCorrectionOut(
        message_id=record.message.id,
        claim_text=record.claim.text,
        verdict=record.message.verdict,
        summary=record.message.summary,
        source=source_out(record.source) if record.source else None,
        translations=[
            PublicTranslationOut(language=loc.language, text=loc.text)
            for loc in record.translations
        ],
        approved_by=record.approved_by,
        approved_at=record.approved_at,
        sealed_at=record.sealed_at,
        integrity_hash=record.integrity_hash,
        previous_hash=record.previous_hash,
        hash_algorithm=record.hash_algorithm,
        canonical_json=record.canonical_json,
        integrity_verified=record.integrity_verified,
    )
