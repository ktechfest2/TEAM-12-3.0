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
