from clarion_api.domain.enums import Language

OGG_CAPTURE_PATTERN = b"OggS"


class FakeSpeechSynthesizer:
    """Returns a tiny deterministic payload that starts like an Ogg file, so the render and
    send paths can be tested without a real voice."""

    async def synthesize(self, text: str, *, language: Language) -> bytes:
        return OGG_CAPTURE_PATTERN + f"FAKEAUDIO:{language.value}:{len(text)}".encode()
