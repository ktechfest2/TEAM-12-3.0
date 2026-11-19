"""Texts approved corrections to confirmed phone subscribers, within their own limits.

Every text goes through `ensure_publishable`, the same rule the broadcast path uses, so an
unapproved or unsealed message is never sent. A subscriber's daily maximum is a hard cap:
corrections over it are held and go out in a later text, never dropped, never over the cap.
"""

from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

from clarion_api.adapters.channels.base import SmsSender
from clarion_api.adapters.crypto import Cipher
from clarion_api.domain.enums import DeliveryMode, DigestFrequency, Language
from clarion_api.domain.errors import NotPublishableError
from clarion_api.domain.models import MasterMessage, SmsSubscription
from clarion_api.domain.rules import ensure_publishable
from clarion_api.observability import get_logger
from clarion_api.repositories.base import MessageRepository, SmsSubscriptionRepository
from clarion_api.services.broadcasting import text_for
from clarion_api.services.rendering.sms import shorten_for_sms

log = get_logger(__name__)

LAGOS = timezone(timedelta(hours=1))  # West Africa Time, no daylight saving
MAX_ITEMS_PER_TEXT = 5
SEEN_LIMIT = 30
INTERVALS = {
    DigestFrequency.HOURLY: timedelta(hours=1),
    DigestFrequency.DAILY: timedelta(days=1),
    DigestFrequency.WEEKLY: timedelta(weeks=1),
}


def _today(now: datetime) -> str:
    return now.astimezone(LAGOS).date().isoformat()


def sent_today(subscription: SmsSubscription, now: datetime) -> int:
    return subscription.sent_today if subscription.sent_on == _today(now) else 0


def _language_for(message: MasterMessage, subscription: SmsSubscription) -> Language | None:
    """The first language the person asked for that this message can be sent in."""
    for language in subscription.preferences.languages:
        try:
            ensure_publishable(message, [language])
        except NotPublishableError:
            continue
        return language
    return None


def _compose(items: list[tuple[MasterMessage, Language]], *, web_url: str) -> str:
    per_item = 2 if len(items) == 1 else 1
    parts = [
        shorten_for_sms(
            text_for(message, language), f"{web_url}/c/{message.id}", max_segments=per_item
        )
        for message, language in items
    ]
    return "\n\n".join(parts) + f"\nStop: {web_url}/subscribe"


def _after_send(
    subscription: SmsSubscription, now: datetime, *, sent: list[UUID]
) -> SmsSubscription:
    held = [i for i in subscription.held_message_ids if i not in sent]
    return subscription.model_copy(
        update={
            "sent_on": _today(now),
            "sent_today": sent_today(subscription, now) + 1,
            "last_sent_at": now,
            "held_message_ids": held,
        }
    )


async def notify_subscribers(
    message: MasterMessage,
    *,
    web_url: str,
    subscriptions: SmsSubscriptionRepository,
    cipher: Cipher,
    sender: SmsSender,
    now: datetime | None = None,
) -> int:
    """Handle one newly broadcast message. Returns how many texts went out right away."""
    now = now or datetime.now(UTC)
    sent = 0
    for subscription in await subscriptions.list_active():
        if message.id in subscription.seen_message_ids:
            continue
        language = _language_for(message, subscription)
        if language is None:
            continue
        seen = [*subscription.seen_message_ids, message.id][-SEEN_LIMIT:]
        prefs = subscription.preferences
        can_send_now = (
            prefs.mode is DeliveryMode.INSTANT and sent_today(subscription, now) < prefs.max_per_day
        )
        if can_send_now:
            try:
                number = cipher.decrypt(subscription.phone_encrypted)
                await sender.send_sms([number], _compose([(message, language)], web_url=web_url))
            except Exception:
                log.warning("sms.subscriber.send_failed", subscription_id=str(subscription.id))
            else:
                updated = _after_send(subscription, now, sent=[])
                await subscriptions.save(updated.model_copy(update={"seen_message_ids": seen}))
                sent += 1
                continue
        held = [*subscription.held_message_ids, message.id]
        await subscriptions.save(
            subscription.model_copy(update={"held_message_ids": held, "seen_message_ids": seen})
        )
    return sent


def _is_due(subscription: SmsSubscription, now: datetime) -> bool:
    prefs = subscription.preferences
    if not subscription.held_message_ids or sent_today(subscription, now) >= prefs.max_per_day:
        return False
    if prefs.mode is DeliveryMode.INSTANT:
        return True  # held only because the cap was reached; a new day has begun
    last = subscription.last_sent_at
    return last is None or now - last >= INTERVALS[prefs.digest_frequency]


async def flush_due(
    *,
    web_url: str,
    messages: MessageRepository,
    subscriptions: SmsSubscriptionRepository,
    cipher: Cipher,
    sender: SmsSender,
    now: datetime | None = None,
) -> int:
    """Send held corrections to everyone whose digest is due. Returns texts sent."""
    now = now or datetime.now(UTC)
    texts = 0
    for subscription in await subscriptions.list_active():
        if not _is_due(subscription, now):
            continue
        items: list[tuple[MasterMessage, Language]] = []
        used: list[UUID] = []
        dropped: list[UUID] = []
        for message_id in subscription.held_message_ids:
            message = await messages.get(message_id)
            language = _language_for(message, subscription) if message else None
            if message is None or language is None:
                dropped.append(message_id)  # retracted or no longer sendable: nothing to say
            elif len(items) < MAX_ITEMS_PER_TEXT:
                items.append((message, language))
                used.append(message_id)
        cleaned = subscription.model_copy(
            update={
                "held_message_ids": [i for i in subscription.held_message_ids if i not in dropped]
            }
        )
        if not items:
            await subscriptions.save(cleaned)
            continue
        try:
            number = cipher.decrypt(subscription.phone_encrypted)
            await sender.send_sms([number], _compose(items, web_url=web_url))
        except Exception:
            log.warning("sms.subscriber.send_failed", subscription_id=str(subscription.id))
            await subscriptions.save(cleaned)
            continue
        await subscriptions.save(_after_send(cleaned, now, sent=used))
        texts += 1
    return texts
