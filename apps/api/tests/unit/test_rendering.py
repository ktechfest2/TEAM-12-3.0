import io
from uuid import UUID

import pytest
from PIL import Image

from clarion_api.adapters.speech.fake import FakeSpeechSynthesizer
from clarion_api.domain.enums import Language, RenditionFormat, Verdict
from clarion_api.domain.errors import NotPublishableError, RenderError
from clarion_api.services.rendering.graphics import (
    CARD_SIZE,
    POSTER_SIZE,
    VERDICT_LABELS,
    poster_pdf,
    qr_image,
    qr_png,
    social_card_png,
)
from clarion_api.services.rendering.service import render_message
from clarion_api.services.rendering.sms import SmsEncoding, measure, shorten_for_sms
from clarion_api.services.rendering.voice import (
    ensure_voice_note,
    looks_like_ogg,
    render_voice_note,
    voice_key,
)
from tests.factories import approved_message

LINK = "https://clarion.example/c/1"
URL = "https://clarion.example/c/00000000-0000-0000-0000-000000000001"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class RecordingStore:
    def __init__(self) -> None:
        self.saved: dict[str, tuple[bytes, str]] = {}

    async def put(self, key: str, data: bytes, *, content_type: str) -> str:
        self.saved[key] = (data, content_type)
        return self.public_url(key)

    async def exists(self, key: str) -> bool:
        return key in self.saved

    def public_url(self, key: str) -> str:
        return f"https://media.example/{key}"


class WrongFormatSpeech:
    async def synthesize(self, text: str, *, language: Language) -> bytes:
        return b"ID3-this-is-an-mp3"


# ---------------------------------------------------------------- SMS


def test_short_text_is_kept_whole_with_the_link() -> None:
    result = shorten_for_sms("INEC did not issue this timetable.", LINK, max_segments=2)
    assert result == f"INEC did not issue this timetable. {LINK}"


def test_long_text_is_cut_at_a_word_and_the_link_is_always_kept() -> None:
    text = "INEC did not issue this timetable and asks everyone to ignore it. " * 6
    result = shorten_for_sms(text, LINK, max_segments=2)
    assert result.endswith(f"... {LINK}")
    assert measure(result).segments <= 2
    assert result.startswith("INEC did not issue")


def test_the_real_ellipsis_character_is_never_used() -> None:
    text = "word " * 100
    assert "…" not in shorten_for_sms(text, LINK, max_segments=1)


def test_yoruba_tone_marks_survive_shortening() -> None:
    text = "Ẹ jọ̀ọ́, ẹ má ṣe gbàgbọ́ ìròyìn yìí. Ìgbìmọ̀ ètò ìdìbò kò gbé àkókò yìí jáde rárá. " * 3
    result = shorten_for_sms(text, LINK, max_segments=2)
    assert measure(result).encoding is SmsEncoding.UCS2
    assert measure(result).segments <= 2
    body = result.removesuffix(f"... {LINK}")
    assert text.startswith(body)  # nothing inside the kept text was altered or stripped
    assert "ẹ" in body or "ọ" in body


def test_when_even_one_word_cannot_fit_only_the_link_is_sent() -> None:
    assert shorten_for_sms("x" * 500, LINK, max_segments=1) == LINK


# ---------------------------------------------------------------- pictures


def test_qr_png_is_a_png_of_the_requested_size() -> None:
    data = qr_png(URL, size=300)
    assert data.startswith(PNG_MAGIC)
    assert Image.open(io.BytesIO(data)).size == (300, 300)


def test_different_links_give_different_qr_codes() -> None:
    assert qr_image(URL, size=200).tobytes() != qr_image(URL + "9", size=200).tobytes()


def test_social_card_is_a_png_that_embeds_the_qr_for_the_public_page() -> None:
    data = social_card_png(
        verdict=Verdict.CONTRADICTED,
        summary="INEC did not issue this timetable.",
        source_name="INEC statement (INEC)",
        public_url=URL,
    )
    assert data.startswith(PNG_MAGIC)
    card = Image.open(io.BytesIO(data)).convert("RGB")
    assert card.size == CARD_SIZE
    margin, qr_size = 70, 330
    top = CARD_SIZE[1] - qr_size - margin
    corner = card.crop((margin, top, margin + qr_size, top + qr_size))
    assert corner.tobytes() == qr_image(URL, size=qr_size).tobytes()


def test_card_band_uses_the_verdict_colour() -> None:
    def band_pixel(verdict: Verdict) -> tuple[int, int, int]:
        png = social_card_png(verdict=verdict, summary="s", source_name="n", public_url=URL)
        pixel = Image.open(io.BytesIO(png)).convert("RGB").getpixel((CARD_SIZE[0] - 5, 5))
        assert isinstance(pixel, tuple)
        return pixel[0], pixel[1], pixel[2]

    colours = {v: band_pixel(v) for v in Verdict}
    assert len(set(colours.values())) == 3


def test_every_verdict_has_a_plain_label_and_only_three_exist() -> None:
    assert set(VERDICT_LABELS) == set(Verdict)
    assert len(Verdict) == 3


def test_poster_is_a_pdf() -> None:
    data = poster_pdf(
        verdict=Verdict.CONFIRMED, summary="Polls open at 8am.", source_name="INEC", public_url=URL
    )
    assert data.startswith(b"%PDF")
    assert b"%%EOF" in data[-64:]
    assert POSTER_SIZE[1] > POSTER_SIZE[0]


# ---------------------------------------------------------------- voice


async def test_voice_note_is_stored_as_ogg() -> None:
    store = RecordingStore()
    url = await render_voice_note(
        "hello",
        language=Language.YORUBA,
        speech=FakeSpeechSynthesizer(),
        store=store,
        key="v/yo.ogg",
    )
    data, content_type = store.saved["v/yo.ogg"]
    assert looks_like_ogg(data)
    assert content_type == "audio/ogg"
    assert url == "https://media.example/v/yo.ogg"


async def test_audio_that_is_not_ogg_is_refused_and_not_stored() -> None:
    store = RecordingStore()
    with pytest.raises(RenderError, match="OGG"):
        await render_voice_note(
            "hello",
            language=Language.HAUSA,
            speech=WrongFormatSpeech(),
            store=store,
            key="v/ha.ogg",
        )
    assert store.saved == {}


class CountingSpeech(FakeSpeechSynthesizer):
    def __init__(self) -> None:
        self.calls = 0

    async def synthesize(self, text: str, *, language: Language) -> bytes:
        self.calls += 1
        return await super().synthesize(text, language=language)


async def test_a_voice_note_is_spoken_once_then_reused() -> None:
    store, speech = RecordingStore(), CountingSpeech()
    message_id = UUID("00000000-0000-0000-0000-000000000001")

    async def ask() -> str:
        return await ensure_voice_note(
            "hello", message_id=message_id, language=Language.YORUBA, speech=speech, store=store
        )

    first, second = await ask(), await ask()
    assert first == second == f"https://media.example/{voice_key(message_id, Language.YORUBA)}"
    assert speech.calls == 1


# ---------------------------------------------------------------- whole message


async def test_a_sealed_message_renders_every_format() -> None:
    store = RecordingStore()
    message = approved_message()
    items = await render_message(
        message,
        [Language.ENGLISH, Language.YORUBA],
        public_url=LINK,
        speech=FakeSpeechSynthesizer(),
        store=store,
    )
    pairs = {(i.language, i.format) for i in items}
    assert pairs == {
        (Language.ENGLISH, RenditionFormat.SMS_TEXT),
        (Language.ENGLISH, RenditionFormat.VOICE_NOTE),
        (Language.YORUBA, RenditionFormat.SMS_TEXT),
        (Language.YORUBA, RenditionFormat.VOICE_NOTE),
        (Language.ENGLISH, RenditionFormat.SOCIAL_CARD),
        (Language.ENGLISH, RenditionFormat.POSTER_PDF),
    }
    sms = {i.language: i.text for i in items if i.format is RenditionFormat.SMS_TEXT}
    assert sms[Language.YORUBA] == f"yo text {LINK}"
    base = f"renditions/{message.id}"
    assert set(store.saved) == {
        f"{base}/voice-en.ogg",
        f"{base}/voice-yo.ogg",
        f"{base}/card.png",
        f"{base}/poster.pdf",
    }
    assert store.saved[f"{base}/card.png"][1] == "image/png"
    assert store.saved[f"{base}/poster.pdf"][1] == "application/pdf"


async def test_an_unreviewed_message_is_never_rendered() -> None:
    store = RecordingStore()
    with pytest.raises(NotPublishableError):
        await render_message(
            approved_message(review=None),
            [Language.ENGLISH],
            public_url=LINK,
            speech=FakeSpeechSynthesizer(),
            store=store,
        )
    assert store.saved == {}


async def test_an_unapproved_translation_is_never_rendered() -> None:
    store = RecordingStore()
    with pytest.raises(NotPublishableError):
        await render_message(
            approved_message(),
            [Language.ENGLISH, Language.HAUSA],
            public_url=LINK,
            speech=FakeSpeechSynthesizer(),
            store=store,
        )
    assert store.saved == {}
