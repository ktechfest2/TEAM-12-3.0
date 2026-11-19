"""Subscriptions by chat command: `JOIN YORUBA` and `STOP`.

An address (for example a Telegram chat id) is never stored. Only a keyed hash
is, so the table cannot be turned back into a contact list.
"""

import hashlib
import hmac
from dataclasses import dataclass

from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.domain.models import Subscriber
from clarion_api.repositories.base import SubscriberRepository

LANGUAGE_WORDS: dict[str, Language] = {
    "en": Language.ENGLISH,
    "english": Language.ENGLISH,
    "yo": Language.YORUBA,
    "yoruba": Language.YORUBA,
    "ha": Language.HAUSA,
    "hausa": Language.HAUSA,
    "ig": Language.IGBO,
    "igbo": Language.IGBO,
    "pcm": Language.PIDGIN,
    "pidgin": Language.PIDGIN,
}


@dataclass(frozen=True)
class JoinCommand:
    language: Language | None  # None means the word after JOIN was missing or unknown


@dataclass(frozen=True)
class StopCommand:
    pass


@dataclass(frozen=True)
class ClaimText:
    text: str


@dataclass(frozen=True)
class IgnoredMessage:
    pass


Command = JoinCommand | StopCommand | ClaimText | IgnoredMessage


def parse_command(raw: str | None) -> Command:
    """Read a chat message. Commands may start with a slash and are case insensitive."""
    text = (raw or "").strip()
    if not text:
        return IgnoredMessage()
    words = text.lstrip("/").split()
    head = words[0].lower().split("@")[0]  # "/join@ClarionBot" arrives as one word
    if head == "stop":
        return StopCommand()
    if head == "join":
        wanted = words[1].lower() if len(words) > 1 else ""
        return JoinCommand(language=LANGUAGE_WORDS.get(wanted))
    if head == "start":
        return IgnoredMessage()
    return ClaimText(text=text)


def address_hash(secret: str, channel: ChannelKind, address: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), f"{channel.value}:{address}".encode(), hashlib.sha256)
    return f"hmac-sha256:{mac.hexdigest()}"


async def join(
    *,
    secret: str,
    channel: ChannelKind,
    address: str,
    language: Language,
    subscribers: SubscriberRepository,
) -> Subscriber:
    """Subscribe, or change language if already subscribed. Records when consent was given."""
    subscriber = Subscriber(
        channel=channel, address_hash=address_hash(secret, channel, address), language=language
    )
    return await subscribers.upsert(subscriber)


async def leave(
    *, secret: str, channel: ChannelKind, address: str, subscribers: SubscriberRepository
) -> bool:
    return await subscribers.remove(channel, address_hash(secret, channel, address))
