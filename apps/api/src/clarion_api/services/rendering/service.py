"""One approved, sealed message to every format a channel needs.

Rendering refuses anything that the publish rules would refuse, so no unreviewed text
is ever turned into a card, poster or voice note.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from clarion_api.adapters.speech.base import SpeechSynthesizer
from clarion_api.adapters.storage.base import ObjectStore
from clarion_api.domain.enums import Language, RenditionFormat
from clarion_api.domain.models import MasterMessage
from clarion_api.domain.rules import ensure_publishable
from clarion_api.services.broadcasting import text_for
from clarion_api.services.rendering.graphics import poster_pdf, social_card_png
from clarion_api.services.rendering.sms import shorten_for_sms
from clarion_api.services.rendering.voice import render_voice_note

SMS_MAX_SEGMENTS = 2
PNG = "image/png"
PDF = "application/pdf"


@dataclass(frozen=True)
class RenderedItem:
    """One produced format. `text` is set for text formats, `media_url` for stored files."""

    language: Language
    format: RenditionFormat
    text: str | None = None
    media_url: str | None = None


def source_name(message: MasterMessage) -> str:
    if message.passage is None:
        return "No official statement found yet"
    return f"{message.passage.document_title} ({message.passage.publisher})"


async def render_message(
    message: MasterMessage,
    languages: Sequence[Language],
    *,
    public_url: str,
    speech: SpeechSynthesizer,
    store: ObjectStore,
) -> list[RenderedItem]:
    """Render SMS text and a voice note per language, plus one social card and one poster.

    Raises NotPublishableError when the message is not approved, sealed and fully translated.
    """
    ensure_publishable(message, languages)
    base = f"renditions/{message.id}"
    items: list[RenderedItem] = []

    for language in languages:
        text = text_for(message, language)
        items.append(
            RenderedItem(
                language,
                RenditionFormat.SMS_TEXT,
                text=shorten_for_sms(text, public_url, max_segments=SMS_MAX_SEGMENTS),
            )
        )
        voice_url = await render_voice_note(
            text, language=language, speech=speech, store=store, key=f"{base}/voice-{language}.ogg"
        )
        items.append(RenderedItem(language, RenditionFormat.VOICE_NOTE, media_url=voice_url))

    verdict, summary, source, link = (
        message.verdict,
        message.summary,
        source_name(message),
        public_url,
    )
    card = social_card_png(verdict=verdict, summary=summary, source_name=source, public_url=link)
    poster = poster_pdf(verdict=verdict, summary=summary, source_name=source, public_url=link)
    card_url = await store.put(f"{base}/card.png", card, content_type=PNG)
    poster_url = await store.put(f"{base}/poster.pdf", poster, content_type=PDF)
    items.append(RenderedItem(Language.ENGLISH, RenditionFormat.SOCIAL_CARD, media_url=card_url))
    items.append(RenderedItem(Language.ENGLISH, RenditionFormat.POSTER_PDF, media_url=poster_url))
    return items
