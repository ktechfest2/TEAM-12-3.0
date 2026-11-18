"""SMS sizing that respects Nigerian language characters.

Yoruba, Igbo and Hausa letters such as ẹ, ọ, ṣ, ɓ and ƙ are outside the GSM 03.38
alphabet, so any message containing them is sent as UCS-2: 70 characters for a
single part, 67 per part when concatenated. Never strip tone marks to save
space; it changes meaning.
"""

from dataclasses import dataclass
from enum import StrEnum
from math import ceil

GSM_BASIC = frozenset(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
)
GSM_EXTENDED = frozenset("^{}\\[~]|€\f")


class SmsEncoding(StrEnum):
    GSM7 = "gsm7"
    UCS2 = "ucs2"


@dataclass(frozen=True, slots=True)
class SmsSize:
    encoding: SmsEncoding
    units: int
    segments: int
    per_segment_limit: int


def _ucs2_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def measure(text: str) -> SmsSize:
    if all(ch in GSM_BASIC or ch in GSM_EXTENDED for ch in text):
        units = sum(2 if ch in GSM_EXTENDED else 1 for ch in text)
        single, multi, encoding = 160, 153, SmsEncoding.GSM7
    else:
        units = _ucs2_units(text)
        single, multi, encoding = 70, 67, SmsEncoding.UCS2

    if units <= single:
        return SmsSize(encoding, units, 1 if units else 0, single)
    return SmsSize(encoding, units, ceil(units / multi), multi)


def fits(text: str, max_segments: int) -> bool:
    return measure(text).segments <= max_segments
