"""Texts people send to our number: claims, JOIN and STOP (ADR 0010).

The gateway SIM is also someone's personal phone, so every text it receives arrives here.
A text is Clarion's only when its first word is CLARION, or when it is a bare STOP from a
number that already has a subscription. Anything else is dropped on arrival: not stored,
not logged, not answered. Replies are fixed text, one plain 160 character text each.
"""

import re
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum

from clarion_api.adapters.channels.base import InboundSms, SmsSender
from clarion_api.adapters.crypto import Cipher
from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import ChannelKind, Language, SubscriptionStatus
from clarion_api.domain.errors import InvalidPhoneError
from clarion_api.domain.models import SmsPreferences, SmsSubscription
from clarion_api.observability import get_logger
from clarion_api.repositories.base import (
    ClaimRepository,
    MessageRepository,
    SmsSubscriptionRepository,
    SourceRepository,
)
from clarion_api.services.intake import submit_claim
from clarion_api.services.messages import create_message
from clarion_api.services.rate_limit import SlidingWindowLimiter
from clarion_api.services.sms_subscriptions import normalize_phone
from clarion_api.services.subscriptions import (
    ClaimText,
    Command,
    IgnoredMessage,
    JoinCommand,
    StopCommand,
    address_hash,
    parse_command,
)

log = get_logger(__name__)

KEYWORD = "clarion"
LANGUAGE_NAMES = {
    Language.ENGLISH: "English",
    Language.YORUBA: "Yoruba",
    Language.HAUSA: "Hausa",
    Language.IGBO: "Igbo",
    Language.PIDGIN: "Pidgin",
}

HELP = (
    "Clarion checks election claims against official statements. Text CLARION then the claim. "
    "For alerts text CLARION JOIN YORUBA, HAUSA, IGBO, PIDGIN or ENGLISH."
)
JOIN_HELP = "Which language? Text CLARION JOIN YORUBA, HAUSA, IGBO, PIDGIN or ENGLISH."
CLAIM_RECEIVED = (
    "Clarion got your claim. A person will check it against official statements. "
    "We only share answers a reviewer approved, with the source."
)
STOPPED = "Clarion: you are removed and your number is deleted. No more texts."
NOT_SUBSCRIBED = "Clarion: this number has no alerts, so there is nothing to stop."
ALERTS_CLOSED = "Clarion text alerts are not open yet. You can still text CLARION and a claim."


def joined_text(language: Language, max_per_day: int) -> str:
    return (
        f"Clarion: you will get approved election corrections in {LANGUAGE_NAMES[language]}, "
        f"at most {max_per_day} texts a day. Text STOP to leave."
    )


class Outcome(StrEnum):
    """What happened to a text. Safe to log: it says nothing about the person or content."""

    NOT_FOR_US = "not_for_us"
    DUPLICATE = "duplicate"
    THROTTLED = "throttled"
    HELP = "help"
    CLAIM = "claim"
    JOINED = "joined"
    STOPPED = "stopped"


@dataclass
class InboxGuard:
    """Duplicate and flood protection, kept in this process (one API process, ADR 0010)."""

    seen_limit: int = 5000
    seen: OrderedDict[str, None] = field(default_factory=OrderedDict)
    per_sender: SlidingWindowLimiter = field(
        default_factory=lambda: SlidingWindowLimiter(limit=5, window=timedelta(hours=1))
    )
    replies_per_sender: SlidingWindowLimiter = field(
        default_factory=lambda: SlidingWindowLimiter(limit=3, window=timedelta(hours=1))
    )
    replies_overall: SlidingWindowLimiter = field(
        default_factory=lambda: SlidingWindowLimiter(limit=100, window=timedelta(days=1))
    )

    def first_time(self, message_id: str) -> bool:
        if message_id in self.seen:
            return False
        self.seen[message_id] = None
        while len(self.seen) > self.seen_limit:
            self.seen.popitem(last=False)
        return True


def read_text(text: str, *, has_subscription: bool) -> Command | None:
    """The command in a text, or None when the text is not meant for Clarion."""
    words = text.strip().split(maxsplit=1)
    if not words:
        return None
    head = re.sub(r"[^a-z]", "", words[0].lower())
    if head == KEYWORD:
        rest = words[1] if len(words) > 1 else ""
        return parse_command(rest)
    if has_subscription and len(words) == 1 and head == "stop":
        return StopCommand()
    return None


@dataclass(frozen=True)
class InboxDeps:
    secret: str
    cipher: Cipher | None
    sender: SmsSender
    claims: ClaimRepository
    sources: SourceRepository
    messages: MessageRepository
    subscriptions: SmsSubscriptionRepository
    llm: LanguageModel
    guard: InboxGuard


@dataclass(frozen=True)
class _Sender:
    """The person who texted, for this one request only. The number is never stored here."""

    phone: str
    phone_hash: str
    subscription: SmsSubscription | None


def _phone_or_none(raw: str) -> str | None:
    try:
        return normalize_phone(raw)
    except InvalidPhoneError:
        return None  # bank, network operator or short code names are never people


async def handle_inbound_sms(sms: InboundSms, deps: InboxDeps, now: datetime) -> Outcome:
    phone = _phone_or_none(sms.sender)
    if phone is None:
        return Outcome.NOT_FOR_US
    phone_hash = address_hash(deps.secret, ChannelKind.SMS, phone)
    subscription = await deps.subscriptions.get_by_hash(phone_hash)
    command = read_text(sms.text, has_subscription=subscription is not None)
    if command is None:
        return Outcome.NOT_FOR_US
    if not deps.guard.first_time(sms.message_id):
        return Outcome.DUPLICATE
    if not deps.guard.per_sender.allow(phone_hash, now):
        return Outcome.THROTTLED
    return await _act(command, _Sender(phone, phone_hash, subscription), deps, now)


async def _act(command: Command, who: _Sender, deps: InboxDeps, now: datetime) -> Outcome:
    if isinstance(command, IgnoredMessage):
        await _reply(deps, who, HELP, now)
        return Outcome.HELP
    if isinstance(command, StopCommand):
        if who.subscription is None:
            await _reply(deps, who, NOT_SUBSCRIBED, now)
        else:
            await deps.subscriptions.delete(who.subscription.id)
            await _reply(deps, who, STOPPED, now)
        return Outcome.STOPPED
    if isinstance(command, JoinCommand):
        return await _join(command.language, who, deps, now)
    claim: ClaimText = command  # the only kind left; mypy fails here if a new one is added
    await _take_claim(claim.text, who.subscription, deps)
    await _reply(deps, who, CLAIM_RECEIVED, now)
    return Outcome.CLAIM


async def _join(language: Language | None, who: _Sender, deps: InboxDeps, now: datetime) -> Outcome:
    if language is None:
        await _reply(deps, who, JOIN_HELP, now)
        return Outcome.HELP
    if deps.cipher is None:
        await _reply(deps, who, ALERTS_CLOSED, now)
        return Outcome.HELP
    joined = _joined(who, language=language, cipher=deps.cipher, now=now)
    await deps.subscriptions.save(joined)
    await _reply(deps, who, joined_text(language, joined.preferences.max_per_day), now)
    return Outcome.JOINED


def _joined(who: _Sender, *, language: Language, cipher: Cipher, now: datetime) -> SmsSubscription:
    """Texting from the number proves control of it, so the subscription is active at once."""
    existing = who.subscription
    if existing is None:
        return SmsSubscription(
            phone_hash=who.phone_hash,
            phone_encrypted=cipher.encrypt(who.phone),
            status=SubscriptionStatus.ACTIVE,
            preferences=SmsPreferences(languages=[language]),
            consented_at=now,
        )
    others = [lang for lang in existing.preferences.languages if lang != language]
    preferences = existing.preferences.model_copy(update={"languages": [language, *others][:5]})
    return existing.model_copy(
        update={
            "status": SubscriptionStatus.ACTIVE,
            "preferences": preferences,
            "requested": None,
            "unsubscribe_requested": False,
            "consented_at": existing.consented_at or now,
            "code_hash": None,
            "code_expires_at": None,
            "code_attempts": 0,
        }
    )


async def _take_claim(text: str, subscription: SmsSubscription | None, deps: InboxDeps) -> None:
    """Store the claim without the sender, and queue a draft for reviewers."""
    language = (
        subscription.preferences.languages[0]
        if subscription and subscription.status is SubscriptionStatus.ACTIVE
        else Language.ENGLISH
    )
    claim, result = await submit_claim(
        text,
        language=language,
        via=ChannelKind.SMS,
        claims=deps.claims,
        sources=deps.sources,
        llm=deps.llm,
    )
    await create_message(
        claim.id,
        claims=deps.claims,
        sources=deps.sources,
        messages=deps.messages,
        llm=deps.llm,
        result=result,
    )


async def _reply(deps: InboxDeps, who: _Sender, text: str, now: datetime) -> None:
    """One text back, unless this number or everyone together is over the reply limit."""
    if not deps.guard.replies_per_sender.allow(who.phone_hash, now):
        return
    if not deps.guard.replies_overall.allow("all", now):
        return
    try:
        await deps.sender.send_sms([who.phone], text)
    except Exception as exc:  # a failed reply must not lose the claim or make the gateway retry
        log.warning("sms_reply_failed", error=type(exc).__name__)
