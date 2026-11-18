import pytest

from clarion_api.services.rendering.sms import SmsEncoding, measure


def test_plain_english_uses_gsm7_single_segment() -> None:
    size = measure("INEC did not issue this timetable.")
    assert size.encoding is SmsEncoding.GSM7
    assert size.segments == 1


def test_extended_characters_count_double() -> None:
    assert measure("[]").units == 4


def test_yoruba_tone_marks_force_ucs2() -> None:
    size = measure("Ẹ jọ̀ọ́, ẹ má ṣe gbàgbọ́ ìròyìn yìí.")
    assert size.encoding is SmsEncoding.UCS2
    assert size.per_segment_limit == 70


@pytest.mark.parametrize(("length", "segments"), [(160, 1), (161, 2), (306, 2), (307, 3)])
def test_gsm7_segment_boundaries(length: int, segments: int) -> None:
    assert measure("a" * length).segments == segments


@pytest.mark.parametrize(("length", "segments"), [(70, 1), (71, 2), (134, 2), (135, 3)])
def test_ucs2_segment_boundaries(length: int, segments: int) -> None:
    assert measure("ẹ" * length).segments == segments


def test_empty_text_has_zero_segments() -> None:
    assert measure("").segments == 0
