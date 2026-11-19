"""Spitch speech generation over plain HTTPS; no SDK, so nothing to lock in.

Endpoint, fields and formats follow the published Spitch Python SDK (spitch 1.50.0):
POST {base}/v1/speech with a bearer key and JSON {text, voice, language, format}.
The response body is the audio itself. We always ask for `ogg_opus`, the format
Telegram and WhatsApp play as a voice note.
"""

from collections.abc import Mapping

import httpx

from clarion_api.domain.enums import Language
from clarion_api.domain.errors import RenderError

DEFAULT_BASE_URL = "https://api.spitch.app"
OUTPUT_FORMAT = "ogg_opus"

# Voices named in the Spitch SDK. Native speakers still have to rate these (T-13);
# override any of them with SPEECH_VOICES, for example {"pcm": "<voice>"}.
DEFAULT_VOICES: Mapping[Language, str] = {
    Language.ENGLISH: "john",
    Language.YORUBA: "sade",
    Language.HAUSA: "amina",
    Language.IGBO: "ngozi",
}

# Spitch does not document a Pidgin voice. Until one is confirmed, Pidgin text is read by
# the English voice with the English language code, unless SPEECH_VOICES names a voice.
LANGUAGE_FALLBACKS: Mapping[Language, Language] = {Language.PIDGIN: Language.ENGLISH}


class SpeechProviderError(RenderError):
    """The provider refused or failed the request. The message never contains the key."""


class SpitchSpeechSynthesizer:
    def __init__(
        self,
        *,
        api_key: str,
        client: httpx.AsyncClient,
        base_url: str | None = None,
        voices: Mapping[Language, str] | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._client = client
        self._url = f"{(base_url or DEFAULT_BASE_URL).rstrip('/')}/v1/speech"
        self._voices = {**DEFAULT_VOICES, **(voices or {})}
        self._timeout = timeout_seconds

    def voice_for(self, language: Language) -> tuple[str, Language]:
        """The voice to use and the language code to send for `language`."""
        if language in self._voices:
            return self._voices[language], language
        fallback = LANGUAGE_FALLBACKS.get(language)
        if fallback is not None and fallback in self._voices:
            return self._voices[fallback], fallback
        msg = f"no speech voice configured for language {language.value}; set SPEECH_VOICES"
        raise SpeechProviderError(msg)

    async def synthesize(self, text: str, *, language: Language) -> bytes:
        voice, spoken_as = self.voice_for(language)
        response = await self._client.post(
            self._url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "text": text,
                "voice": voice,
                "language": spoken_as.value,
                "format": OUTPUT_FORMAT,
            },
            timeout=self._timeout,
        )
        if response.is_error:
            detail = response.text[:200] if response.text else response.reason_phrase
            msg = f"speech provider returned {response.status_code}: {detail}"
            raise SpeechProviderError(msg)
        return response.content
