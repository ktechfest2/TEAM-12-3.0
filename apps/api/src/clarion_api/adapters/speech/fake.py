from clarion_api.domain.enums import Language


class FakeSpeechSynthesizer:
    """Returns a tiny deterministic payload so render and send paths can be tested."""

    async def synthesize(self, text: str, *, language: Language) -> bytes:
        return f"FAKEAUDIO:{language.value}:{len(text)}".encode()
