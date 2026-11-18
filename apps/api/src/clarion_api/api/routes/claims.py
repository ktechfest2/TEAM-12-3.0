from fastapi import APIRouter, status

from clarion_api.api.deps import ContainerDep
from clarion_api.api.schemas import ClaimIn, ClaimOut, SourceOut
from clarion_api.domain.models import Claim
from clarion_api.services.matching import match_claim

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("", status_code=status.HTTP_201_CREATED, operation_id="createClaim")
async def create_claim(body: ClaimIn, container: ContainerDep) -> ClaimOut:
    claim = Claim(text=body.text, language=body.language)
    await container.claims.add(claim)
    result = await match_claim(claim, llm=container.llm, sources=container.sources)
    passage = await container.sources.get(result.passage_id) if result.passage_id else None
    return ClaimOut(
        id=claim.id,
        text=claim.text,
        language=claim.language,
        created_at=claim.created_at,
        verdict=result.verdict,
        rationale=result.rationale,
        confidence=result.confidence,
        source=SourceOut(
            id=passage.id,
            document_title=passage.document_title,
            publisher=passage.publisher,
            url=str(passage.url),
            text=passage.text,
        )
        if passage
        else None,
    )
