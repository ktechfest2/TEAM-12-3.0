from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from clarion_api.api.deps import ContainerDep
from clarion_api.api.mappers import source_out
from clarion_api.api.schemas import PublicCorrectionOut, PublicTranslationOut
from clarion_api.domain.enums import Language
from clarion_api.domain.errors import NotFoundError, RenderError
from clarion_api.services.broadcasting import text_for
from clarion_api.services.public_record import load_public_record
from clarion_api.services.rendering.voice import ensure_voice_note

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


@router.get(
    "/corrections/{message_id}/voice/{language}",
    operation_id="getPublicVoiceNote",
    status_code=302,
    response_class=RedirectResponse,
    responses={302: {"description": "Redirects to the voice note (OGG Opus)."}},
)
async def get_public_voice_note(
    message_id: UUID, language: Language, container: ContainerDep
) -> RedirectResponse:
    """No sign in. Speaks an approved, sealed correction in one of its approved languages.

    The audio is made the first time someone asks and stored, so the speech service is
    called at most once for each message and language. Anything not approved is a 404.
    """
    record = await load_public_record(
        message_id,
        messages=container.messages,
        claims=container.claims,
        audit=container.audit,
    )
    try:
        text = text_for(record.message, language)
    except LookupError as err:
        msg = "this correction has no approved text in that language"
        raise NotFoundError(msg) from err
    try:
        url = await ensure_voice_note(
            text,
            message_id=record.message.id,
            language=language,
            speech=container.speech,
            store=container.store,
        )
    except RenderError as err:
        raise HTTPException(status_code=503, detail="Audio is not available right now.") from err
    return RedirectResponse(url, status_code=302)
