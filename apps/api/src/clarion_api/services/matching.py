"""Claim to verdict. Retrieves official passages, then asks the language model to
choose one of three verdicts and cite a passage. The model never sees the
internet and never invents a source: it may only cite a retrieved passage.
"""

from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import Verdict
from clarion_api.domain.models import Claim, VerdictResult
from clarion_api.repositories.base import SourceRepository

TOP_K_PASSAGES = 5
MIN_CONFIDENCE = 0.6


async def match_claim(
    claim: Claim, *, llm: LanguageModel, sources: SourceRepository
) -> VerdictResult:
    [query_vector] = await llm.embed([claim.text])
    candidates = await sources.search(query_vector, limit=TOP_K_PASSAGES)
    if not candidates:
        return VerdictResult(
            verdict=Verdict.NO_OFFICIAL_STATEMENT,
            passage_id=None,
            rationale="No official passage was found for this claim.",
            confidence=1.0,
        )

    result = await llm.judge_claim(claim.text, candidates)

    cited_ids = {p.id for p in candidates}
    cites_valid_passage = result.passage_id in cited_ids
    if result.verdict is Verdict.NO_OFFICIAL_STATEMENT:
        return result
    if not cites_valid_passage or result.confidence < MIN_CONFIDENCE:
        return VerdictResult(
            verdict=Verdict.NO_OFFICIAL_STATEMENT,
            passage_id=None,
            rationale="The model could not tie this claim to a retrieved official passage.",
            confidence=result.confidence,
        )
    return result
