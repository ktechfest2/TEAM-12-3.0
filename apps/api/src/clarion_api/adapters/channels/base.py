from typing import Protocol

from clarion_api.domain.enums import ChannelKind


class Channel(Protocol):
    kind: ChannelKind

    async def send_text(self, text: str) -> str:
        """Send and return the provider's message id. Raise on failure."""
        ...
