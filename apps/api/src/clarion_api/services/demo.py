"""Known data for the live demo, and the rules for resetting to it.

The claims here are the exact ones used in docs/product/demo-script.md. A test pins
the verdict each one gets from the offline model, so the script cannot drift from the code.
"""

from dataclasses import dataclass

from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.config import AppEnv, Settings
from clarion_api.domain.enums import ChannelKind, Language, Verdict
from clarion_api.domain.errors import DomainError
from clarion_api.domain.models import MasterMessage
from clarion_api.repositories.base import ClaimRepository, MessageRepository, SourceRepository
from clarion_api.services.intake import submit_claim
from clarion_api.services.messages import create_message


class ResetNotAllowedError(DomainError):
    """Raised when a demo reset would be unsafe (production, wrong backend, no confirmation)."""


@dataclass(frozen=True)
class DemoClaim:
    text: str
    expected_verdict: Verdict
    note: str


# Queued before the demo starts, so the reviewer queue is not empty.
QUEUED_CLAIMS: tuple[DemoClaim, ...] = (
    DemoClaim(
        text="INEC has released a new 2027 campaign timetable graphic",
        expected_verdict=Verdict.CONTRADICTED,
        note="Main demo claim. The fake timetable INEC said it never issued.",
    ),
    DemoClaim(
        text="The presidential election is scheduled for 16 January 2027",
        expected_verdict=Verdict.CONFIRMED,
        note="Shows the answer can also confirm something true, with the official source.",
    ),
)

# Typed live by the presenter, so judges see a claim arrive from outside.
LIVE_CLAIM = DemoClaim(
    text="Nigerians abroad can cast ballots through a mobile phone app",
    expected_verdict=Verdict.NO_OFFICIAL_STATEMENT,
    note="A topical claim with no official statement in the sources: Clarion says so, not guesses.",
)


def ensure_reset_allowed(settings: Settings, *, confirmed: bool) -> None:
    """A reset deletes claims, messages, reviews, deliveries and subscribers."""
    if settings.app_env is AppEnv.PRODUCTION:
        msg = "refusing to reset demo data when APP_ENV=production"
        raise ResetNotAllowedError(msg)
    if settings.repository_backend != "sql":
        msg = "demo data lives in Postgres; set REPOSITORY_BACKEND=sql to reset it"
        raise ResetNotAllowedError(msg)
    if not confirmed:
        msg = "this deletes claims, messages, reviews, deliveries and subscribers; pass --yes"
        raise ResetNotAllowedError(msg)


async def queue_demo_claims(
    *,
    claims: ClaimRepository,
    sources: SourceRepository,
    messages: MessageRepository,
    llm: LanguageModel,
) -> list[MasterMessage]:
    """Store the queued demo claims and a draft message for each, ready for the reviewer."""
    drafts: list[MasterMessage] = []
    for demo in QUEUED_CLAIMS:
        claim, result = await submit_claim(
            demo.text,
            language=Language.ENGLISH,
            via=ChannelKind.WEB_FEED,
            claims=claims,
            sources=sources,
            llm=llm,
        )
        drafts.append(
            await create_message(
                claim.id, claims=claims, sources=sources, messages=messages, llm=llm, result=result
            )
        )
    return drafts
