import json

import httpx
import pytest

from clarion_api.adapters.speech import build_speech
from clarion_api.adapters.speech.fake import FakeSpeechSynthesizer
from clarion_api.adapters.speech.spitch import SpeechProviderError, SpitchSpeechSynthesizer
from clarion_api.config import AppEnv, Settings
from clarion_api.domain.enums import Language
from clarion_api.services.rendering.voice import looks_like_ogg

TEST_KEY = "test-key-not-real"
OGG_AUDIO = b"OggS\x00\x02fake-opus-page"


def _recording_client(seen: list[httpx.Request], response: httpx.Response) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return response

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_yoruba_text_is_sent_as_ogg_opus_with_a_yoruba_voice() -> None:
    seen: list[httpx.Request] = []
    async with _recording_client(seen, httpx.Response(200, content=OGG_AUDIO)) as client:
        speech = SpitchSpeechSynthesizer(api_key=TEST_KEY, client=client)
        audio = await speech.synthesize("INEC ko kede eyi.", language=Language.YORUBA)

    assert audio == OGG_AUDIO
    assert looks_like_ogg(audio)
    request = seen[0]
    assert str(request.url) == "https://api.spitch.app/v1/speech"
    assert request.headers["Authorization"] == f"Bearer {TEST_KEY}"
    assert json.loads(request.content) == {
        "text": "INEC ko kede eyi.",
        "voice": "sade",
        "language": "yo",
        "format": "ogg_opus",
    }


async def test_pidgin_falls_back_to_the_english_voice_until_one_is_configured() -> None:
    seen: list[httpx.Request] = []
    async with _recording_client(seen, httpx.Response(200, content=OGG_AUDIO)) as client:
        speech = SpitchSpeechSynthesizer(api_key=TEST_KEY, client=client)
        await speech.synthesize("INEC no talk am.", language=Language.PIDGIN)

    body = json.loads(seen[0].content)
    assert body["voice"] == "john"
    assert body["language"] == "en"


async def test_a_configured_voice_overrides_the_default_and_keeps_its_language() -> None:
    seen: list[httpx.Request] = []
    async with _recording_client(seen, httpx.Response(200, content=OGG_AUDIO)) as client:
        speech = SpitchSpeechSynthesizer(
            api_key=TEST_KEY,
            client=client,
            base_url="https://speech.example.test/",
            voices={Language.PIDGIN: "tega"},
        )
        await speech.synthesize("INEC no talk am.", language=Language.PIDGIN)

    assert str(seen[0].url) == "https://speech.example.test/v1/speech"
    body = json.loads(seen[0].content)
    assert body["voice"] == "tega"
    assert body["language"] == "pcm"


async def test_a_provider_error_is_raised_without_the_key() -> None:
    seen: list[httpx.Request] = []
    refused = httpx.Response(401, json={"detail": "invalid api key"})
    async with _recording_client(seen, refused) as client:
        speech = SpitchSpeechSynthesizer(api_key=TEST_KEY, client=client)
        with pytest.raises(SpeechProviderError, match="401") as caught:
            await speech.synthesize("text", language=Language.HAUSA)

    assert TEST_KEY not in str(caught.value)


async def test_the_factory_builds_spitch_outside_tests_and_needs_a_key() -> None:
    # model_validate skips environment and .env loading, so the VM's own variables cannot leak in.
    async with httpx.AsyncClient() as client:
        settings = Settings.model_validate(
            {
                "app_env": AppEnv.DEVELOPMENT,
                "speech_provider": "spitch",
                "speech_api_key": TEST_KEY,
                "speech_voices": {"pcm": "tega"},
            }
        )
        speech = build_speech(settings, client)
        assert isinstance(speech, SpitchSpeechSynthesizer)
        assert speech.voice_for(Language.PIDGIN) == ("tega", Language.PIDGIN)

        keyless = Settings.model_validate(
            {"app_env": AppEnv.DEVELOPMENT, "speech_provider": "spitch"}
        )
        with pytest.raises(RuntimeError, match="SPEECH_API_KEY"):
            build_speech(keyless, client)


async def test_tests_always_get_the_offline_fake() -> None:
    async with httpx.AsyncClient() as client:
        settings = Settings.model_validate(
            {"app_env": AppEnv.TEST, "speech_provider": "spitch", "speech_api_key": TEST_KEY}
        )
        assert isinstance(build_speech(settings, client), FakeSpeechSynthesizer)
