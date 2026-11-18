from typing import Protocol

from clarion_api.domain.enums import Language


class SpeechSynthesizer(Protocol):
    async def synthesize(self, text: str, *, language: Language) -> bytes:
        """Return audio bytes (OGG Opus preferred: Telegram and WhatsApp play it natively)."""
        ...
