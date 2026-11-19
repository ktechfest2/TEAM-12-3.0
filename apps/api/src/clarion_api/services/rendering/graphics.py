"""Pictures for sharing: the QR code, the social card and the printable poster.

Everything is drawn with Pillow, so there is no browser or extra service to run. Text on
the card and poster is English (verdict, summary, source name). Translations travel as SMS
text and voice notes; drawing them needs a font that covers every tone mark, which is a
separate asset decision.
"""

import io

import qrcode
from PIL import Image, ImageDraw, ImageFont

from clarion_api.domain.enums import Verdict

# Plain words for the three verdicts. Keep in step with apps/web/src/features/claims/verdict.ts.
VERDICT_LABELS: dict[Verdict, str] = {
    Verdict.CONFIRMED: "Confirmed by an official source",
    Verdict.CONTRADICTED: "Contradicted by an official source",
    Verdict.NO_OFFICIAL_STATEMENT: "No official statement found yet",
}

_VERDICT_COLOURS: dict[Verdict, str] = {
    Verdict.CONFIRMED: "#0a7d55",
    Verdict.CONTRADICTED: "#b42318",
    Verdict.NO_OFFICIAL_STATEMENT: "#5b6470",
}

CARD_SIZE = (1080, 1080)
POSTER_SIZE = (1240, 1754)  # A4 at 150 dpi
Font = ImageFont.FreeTypeFont | ImageFont.ImageFont
_INK = "#111827"
_PAPER = "#ffffff"


def qr_image(url: str, *, size: int) -> Image.Image:
    """A QR code for `url`, scaled to a square of `size` pixels, black on white."""
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    code.add_data(url)
    code.make(fit=True)
    image: Image.Image = code.make_image(fill_color="black", back_color="white").convert("RGB")
    return image.resize((size, size), Image.Resampling.NEAREST)


def qr_png(url: str, *, size: int = 512) -> bytes:
    buffer = io.BytesIO()
    qr_image(url, size=size).save(buffer, format="PNG")
    return buffer.getvalue()


def _font(size: int) -> Font:
    return ImageFont.load_default(size=size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: Font, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _paragraph(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    x: int,
    y: int,
    width: int,
    size: int,
    colour: str = _INK,
    max_lines: int = 6,
) -> int:
    """Draw wrapped text and return the y position below it. Overlong text ends with '...'."""
    font = _font(size)
    lines = _wrap(draw, text, font, width)
    if len(lines) > max_lines:
        lines = [*lines[: max_lines - 1], f"{lines[max_lines - 1]}..."]
    for line in lines:
        draw.text((x, y), line, font=font, fill=colour)
        y += int(size * 1.3)
    return y


def _compose(
    canvas_size: tuple[int, int],
    *,
    verdict: Verdict,
    summary: str,
    source_name: str,
    public_url: str,
    scale: float,
) -> Image.Image:
    width, height = canvas_size
    margin = int(70 * scale)
    image = Image.new("RGB", canvas_size, _PAPER)
    draw = ImageDraw.Draw(image)

    band = int(190 * scale)
    draw.rectangle((0, 0, width, band), fill=_VERDICT_COLOURS[verdict])
    draw.text((margin, int(50 * scale)), "CLARION", font=_font(int(34 * scale)), fill="#ffffff")
    _paragraph(
        draw,
        VERDICT_LABELS[verdict],
        x=margin,
        y=int(100 * scale),
        width=width - 2 * margin,
        size=int(52 * scale),
        colour="#ffffff",
        max_lines=1,
    )

    y = band + int(60 * scale)
    y = _paragraph(
        draw, summary, x=margin, y=y, width=width - 2 * margin, size=int(54 * scale), max_lines=7
    )

    qr_size = int(330 * scale)
    qr_top = height - qr_size - margin
    image.paste(qr_image(public_url, size=qr_size), (margin, qr_top))
    text_x = margin + qr_size + int(40 * scale)
    text_width = width - text_x - margin
    ty = _paragraph(
        draw,
        "Official source",
        x=text_x,
        y=qr_top,
        width=text_width,
        size=int(30 * scale),
        colour="#5b6470",
        max_lines=1,
    )
    ty = _paragraph(
        draw, source_name, x=text_x, y=ty, width=text_width, size=int(40 * scale), max_lines=3
    )
    _paragraph(
        draw,
        "Scan to see the source and check this is real",
        x=text_x,
        y=ty + int(20 * scale),
        width=text_width,
        size=int(30 * scale),
        colour="#5b6470",
        max_lines=3,
    )
    return image


def social_card_png(*, verdict: Verdict, summary: str, source_name: str, public_url: str) -> bytes:
    image = _compose(
        CARD_SIZE,
        verdict=verdict,
        summary=summary,
        source_name=source_name,
        public_url=public_url,
        scale=1.0,
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def poster_pdf(*, verdict: Verdict, summary: str, source_name: str, public_url: str) -> bytes:
    image = _compose(
        POSTER_SIZE,
        verdict=verdict,
        summary=summary,
        source_name=source_name,
        public_url=public_url,
        scale=1.15,
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PDF", resolution=150.0)
    return buffer.getvalue()
