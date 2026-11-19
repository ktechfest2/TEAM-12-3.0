"""Fan out: one approved message to every enabled channel, one delivery per
channel and language. Each send runs as its own queued job so one failing
channel never blocks the others."""

from collections.abc import Iterable

from clarion_api.adapters.channels.base import Channel
from clarion_api.domain.enums import DeliveryStatus, Language
from clarion_api.domain.models import Delivery, MasterMessage, utc_now
from clarion_api.domain.rules import ensure_publishable


def text_for(message: MasterMessage, language: Language) -> str:
    if language is Language.ENGLISH:
        return message.summary
    for loc in message.localisations:
        if loc.language is language and loc.is_approved:
            return loc.text
    msg = f"no approved text for {language}"
    raise LookupError(msg)


def plan_deliveries(
    message: MasterMessage, channels: Iterable[Channel], languages: Iterable[Language]
) -> list[Delivery]:
    langs = list(languages)
    ensure_publishable(message, langs)
    return [
        Delivery(message_id=message.id, channel=channel.kind, language=lang)
        for channel in channels
        for lang in langs
    ]


async def send_one(
    message: MasterMessage, delivery: Delivery, channel: Channel, public_url: str
) -> Delivery:
    body = f"{text_for(message, delivery.language)}\n\nSource and details: {public_url}"
    try:
        external_id = await channel.send_text(body)
    except Exception as exc:
        return delivery.model_copy(update={"status": DeliveryStatus.FAILED, "error": str(exc)})
    return delivery.model_copy(
        update={
            "status": DeliveryStatus.SENT,
            "external_id": external_id,
            "sent_at": utc_now(),
        }
    )
