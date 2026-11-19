"""One door for claims. The web form and the Telegram bot both come through here."""

from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.domain.models import Claim, VerdictResult
from clarion_api.repositories.base import ClaimRepository, SourceRepository
from clarion_api.services.matching import match_claim


async def submit_claim(
    text: str,
    *,
    language: Language,
    via: ChannelKind,
    claims: ClaimRepository,
    sources: SourceRepository,
    llm: LanguageModel,
) -> tuple[Claim, VerdictResult]:
    """Store the claim and match it to official passages. The result is a draft for review."""
    claim = Claim(text=text, language=language, submitted_via=via)
    await claims.add(claim)
    result = await match_claim(claim, llm=llm, sources=sources)
    return claim, result
