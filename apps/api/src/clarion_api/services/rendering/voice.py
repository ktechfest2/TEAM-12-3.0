"""Voice notes. The speech adapter returns audio; this checks it is an Ogg container
(Opus inside) so Telegram and WhatsApp play it as a voice note, then stores it."""

from clarion_api.adapters.speech.base import SpeechSynthesizer
from clarion_api.adapters.storage.base import ObjectStore
from clarion_api.domain.enums import Language
from clarion_api.domain.errors import RenderError

OGG_MAGIC = b"OggS"
OGG_CONTENT_TYPE = "audio/ogg"


def looks_like_ogg(audio: bytes) -> bool:
    return audio.startswith(OGG_MAGIC)


async def render_voice_note(
    text: str, *, language: Language, speech: SpeechSynthesizer, store: ObjectStore, key: str
) -> str:
    """Speak `text` and store it under `key`. Returns the public URL of the stored file."""
    audio = await speech.synthesize(text, language=language)
    if not looks_like_ogg(audio):
        msg = "the speech provider did not return OGG audio; configure it for OGG Opus output"
        raise RenderError(msg)
    return await store.put(key, audio, content_type=OGG_CONTENT_TYPE)
