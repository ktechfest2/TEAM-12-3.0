import httpx

from clarion_api.adapters.speech.base import SpeechSynthesizer
from clarion_api.adapters.speech.fake import FakeSpeechSynthesizer
from clarion_api.config import Settings


def build_speech(settings: Settings, http: httpx.AsyncClient) -> SpeechSynthesizer:
    if settings.speech_provider == "fake" or settings.is_test:
        return FakeSpeechSynthesizer()
    if settings.speech_provider == "spitch":
        from clarion_api.adapters.speech.spitch import SpitchSpeechSynthesizer  # noqa: PLC0415

        if settings.speech_api_key is None:
            msg = "SPEECH_API_KEY is required for SPEECH_PROVIDER=spitch"
            raise RuntimeError(msg)
        return SpitchSpeechSynthesizer(
            api_key=settings.speech_api_key.get_secret_value(),
            client=http,
            base_url=settings.speech_base_url,
            voices=settings.speech_voices,
            timeout_seconds=settings.speech_timeout_seconds,
        )
    msg = f"unknown SPEECH_PROVIDER: {settings.speech_provider}"
    raise RuntimeError(msg)


__all__ = ["SpeechSynthesizer", "build_speech"]
