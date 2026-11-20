from fastapi import APIRouter, status

from clarion_api.api.deps import ContainerDep
from clarion_api.api.mappers import source_out
from clarion_api.api.schemas import ClaimIn, ClaimOut
from clarion_api.domain.enums import ChannelKind
from clarion_api.services.intake import submit_claim
from clarion_api.services.messages import create_message

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("", status_code=status.HTTP_201_CREATED, operation_id="createClaim")
async def create_claim(body: ClaimIn, container: ContainerDep) -> ClaimOut:
    claim, result = await submit_claim(
        body.text,
        language=body.language,
        via=ChannelKind.WEB_FEED,
        claims=container.claims,
        sources=container.sources,
        llm=container.llm,
    )
    await create_message(
        claim.id,
        claims=container.claims,
        sources=container.sources,
        messages=container.messages,
        llm=container.llm,
        result=result,
    )
    passage = await container.sources.get(result.passage_id) if result.passage_id else None
    return ClaimOut(
        id=claim.id,
        text=claim.text,
        language=claim.language,
        created_at=claim.created_at,
        verdict=result.verdict,
        rationale=result.rationale,
        confidence=result.confidence,
        source=source_out(passage) if passage else None,
    )
