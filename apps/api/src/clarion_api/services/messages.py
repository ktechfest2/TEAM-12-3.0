"""The review workflow around a master message.

Create it from a claim, review it, localise it, seal it, broadcast it, retract it.
Every change that alters what people would read clears the integrity seal, so a
message can only be published as exactly what was approved.
"""

from collections.abc import Iterable, Sequence
from uuid import UUID

from clarion_api.adapters.channels.base import Channel
from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import ChannelKind, DeliveryStatus, Language, ReviewStatus
from clarion_api.domain.errors import NotFoundError, NotPublishableError
from clarion_api.domain.models import (
    Delivery,
    Localisation,
    MasterMessage,
    Review,
    VerdictResult,
)
from clarion_api.repositories.base import (
    ClaimRepository,
    DeliveryRepository,
    MessageRepository,
    SourceRepository,
)
from clarion_api.services.broadcasting import plan_deliveries
from clarion_api.services.integrity import seal
from clarion_api.services.localisation import draft_localisations
from clarion_api.services.matching import match_claim


async def load_message(message_id: UUID, messages: MessageRepository) -> MasterMessage:
    message = await messages.get(message_id)
    if message is None:
        msg = f"message {message_id} not found"
        raise NotFoundError(msg)
    return message


async def create_message(
    claim_id: UUID,
    *,
    claims: ClaimRepository,
    sources: SourceRepository,
    messages: MessageRepository,
    llm: LanguageModel,
    result: VerdictResult | None = None,
) -> MasterMessage:
    """Store the draft answer for review. Pass `result` to reuse a match already made."""
    claim = await claims.get(claim_id)
    if claim is None:
        msg = f"claim {claim_id} not found"
        raise NotFoundError(msg)
    if result is None:
        result = await match_claim(claim, llm=llm, sources=sources)
    passage = await sources.get(result.passage_id) if result.passage_id else None
    message = MasterMessage(
        claim_id=claim.id,
        verdict=result.verdict,
        passage=passage,
        summary=result.rationale,
        confidence=result.confidence,
    )
    await messages.save(message)
    return message


async def add_review(
    message_id: UUID,
    *,
    reviewer_id: str,
    status: ReviewStatus,
    note: str | None,
    summary: str | None,
    messages: MessageRepository,
) -> MasterMessage:
    """Record a reviewer decision. Editing the summary voids translations and the seal."""
    message = await load_message(message_id, messages)
    changes: dict[str, object] = {
        "review": Review(
            claim_id=message.claim_id, reviewer_id=reviewer_id, status=status, note=note
        ),
        "integrity_hash": None,
    }
    if summary is not None and summary != message.summary:
        changes["summary"] = summary
        changes["localisations"] = ()
    updated = message.model_copy(update=changes)
    await messages.save(updated)
    return updated


async def set_localisation(
    message_id: UUID,
    *,
    language: Language,
    text: str | None,
    messages: MessageRepository,
    llm: LanguageModel,
) -> MasterMessage:
    """Add or replace the draft for one language. Without text, the model drafts it.

    A new or changed draft is always unapproved until a native speaker approves it.
    """
    if language is Language.ENGLISH:
        msg = "English is the master text; it needs no localisation"
        raise NotPublishableError(msg)
    message = await load_message(message_id, messages)
    if text is None:
        [draft] = await draft_localisations(message, [language], llm=llm)
    else:
        draft = Localisation(language=language, text=text)
    kept = tuple(loc for loc in message.localisations if loc.language is not language)
    updated = message.model_copy(update={"localisations": (*kept, draft), "integrity_hash": None})
    await messages.save(updated)
    return updated


async def approve_localisation(
    message_id: UUID, *, language: Language, approved_by: str, messages: MessageRepository
) -> MasterMessage:
    message = await load_message(message_id, messages)
    target = next((loc for loc in message.localisations if loc.language is language), None)
    if target is None:
        msg = f"no {language.value} localisation to approve"
        raise NotFoundError(msg)
    approved = target.model_copy(update={"approved_by": approved_by})
    localisations = tuple(approved if loc.id == target.id else loc for loc in message.localisations)
    updated = message.model_copy(update={"localisations": localisations, "integrity_hash": None})
    await messages.save(updated)
    return updated


async def seal_message(message_id: UUID, *, messages: MessageRepository) -> MasterMessage:
    """Freeze an approved message and chain its hash to the previous sealed message."""
    message = await load_message(message_id, messages)
    if message.review is None or message.review.status is not ReviewStatus.APPROVED:
        msg = "only a message with an approved review can be sealed"
        raise NotPublishableError(msg)
    previous = await messages.latest_integrity_hash(excluding=message.id)
    sealed = seal(message, previous)
    await messages.save(sealed)
    return sealed


def broadcast_languages(
    message: MasterMessage, requested: Sequence[Language] | None
) -> list[Language]:
    """English plus every approved localisation, unless the caller names languages."""
    if requested:
        return list(dict.fromkeys(requested))
    approved = [loc.language for loc in message.localisations if loc.is_approved]
    return [Language.ENGLISH, *dict.fromkeys(approved)]


async def plan_broadcast(
    message_id: UUID,
    *,
    languages: Sequence[Language] | None,
    channels: Iterable[Channel],
    messages: MessageRepository,
    deliveries: DeliveryRepository,
) -> list[Delivery]:
    """Run the publish rules and store one queued delivery per channel and language.

    Raises NotPublishableError before anything is stored when a rule fails.
    """
    message = await load_message(message_id, messages)
    planned = plan_deliveries(message, channels, broadcast_languages(message, languages))
    for delivery in planned:
        await deliveries.save(delivery)
    return planned


def retraction_text(message: MasterMessage, reason: str, public_url: str) -> str:
    return (
        "Correction notice from Clarion: an earlier message on this topic has been withdrawn.\n"
        f"Reason: {reason}\n"
        f"Details: {public_url}\n"
        f"(Earlier message: {message.summary})"
    )


async def retract_message(
    message_id: UUID,
    *,
    reason: str,
    public_url: str,
    channels: Iterable[Channel],
    messages: MessageRepository,
    deliveries: DeliveryRepository,
) -> list[Delivery]:
    """Send a withdrawal notice on every channel that carried the message, then mark them."""
    message = await load_message(message_id, messages)
    by_kind = {channel.kind: channel for channel in channels}
    notice = retraction_text(message, reason, public_url)
    notified: set[ChannelKind] = set()
    result: list[Delivery] = []
    for delivery in await deliveries.list_for_message(message.id):
        if delivery.status is not DeliveryStatus.SENT:
            result.append(delivery)
            continue
        channel = by_kind.get(delivery.channel)
        error: str | None = None
        if channel is not None and delivery.channel not in notified:
            try:
                await channel.send_text(notice)
                notified.add(delivery.channel)
            except Exception as exc:
                error = f"retraction notice failed: {exc}"
        updated = delivery.model_copy(update={"status": DeliveryStatus.RETRACTED, "error": error})
        await deliveries.save(updated)
        result.append(updated)
    return result


__all__ = [
    "add_review",
    "approve_localisation",
    "broadcast_languages",
    "create_message",
    "load_message",
    "plan_broadcast",
    "retract_message",
    "retraction_text",
    "seal_message",
    "set_localisation",
]
