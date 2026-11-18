from clarion_api.adapters.speech.base import SpeechSynthesizer
from clarion_api.adapters.speech.fake import FakeSpeechSynthesizer
from clarion_api.config import Settings


def build_speech(settings: Settings) -> SpeechSynthesizer:
    # Add real providers here once their adapter exists (see docs/tasks).
    if settings.speech_provider == "fake" or settings.is_test:
        return FakeSpeechSynthesizer()
    msg = f"unknown SPEECH_PROVIDER: {settings.speech_provider}"
    raise RuntimeError(msg)


__all__ = ["SpeechSynthesizer", "build_speech"]
