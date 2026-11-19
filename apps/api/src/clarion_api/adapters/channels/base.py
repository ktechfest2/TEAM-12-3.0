from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from clarion_api.domain.enums import ChannelKind


class Channel(Protocol):
    kind: ChannelKind

    async def send_text(self, text: str) -> str:
        """Send and return the provider's message id. Raise on failure."""
        ...


@runtime_checkable
class Replier(Protocol):
    """A channel that can answer one person in a conversation (not a broadcast)."""

    async def reply(self, recipient: str, text: str) -> str:
        """Send `text` to `recipient` and return the provider's message id. Raise on failure."""
        ...


@runtime_checkable
class SmsSender(Protocol):
    """A channel that can text specific numbers (subscribers, verification codes)."""

    async def send_sms(self, numbers: list[str], text: str) -> str:
        """Send `text` to every number and return a provider reference. Raise on failure."""
        ...


@dataclass(frozen=True, slots=True)
class InboundSms:
    """One text a person sent to our number. `message_id` is the gateway's id for the text."""

    message_id: str
    sender: str
    text: str


@runtime_checkable
class InboundSmsReader(Protocol):
    """Reads a gateway webhook: checks it really came from our gateway, then parses it."""

    def read(self, body: bytes, headers: Mapping[str, str], now: datetime) -> InboundSms | None:
        """Return the text, or None for events we do not act on.

        Raise NotAuthorizedError when the signature is missing, wrong or too old.
        """
        ...
