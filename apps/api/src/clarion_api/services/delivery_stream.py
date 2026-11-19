"""Turns stored delivery receipts into a stream of changes for the broadcast board.

It only reads what the repository holds, so a tile can turn green only after a
worker has really sent the message and saved the receipt. Nothing is simulated.
Reading the shared store (instead of an in-process bus) also works when the API
and the worker run as separate processes.
"""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from clarion_api.domain.enums import DeliveryStatus
from clarion_api.domain.models import Delivery
from clarion_api.repositories.base import DeliveryRepository

POLL_SECONDS = 0.5
PING_SECONDS = 15.0
MAX_SECONDS = 600.0

EventName = Literal["snapshot", "delivery", "ping", "done"]
Sleep = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class DeliveryEvent:
    name: EventName
    deliveries: tuple[Delivery, ...] = ()


def _fingerprint(delivery: Delivery) -> tuple[DeliveryStatus, str | None, str | None]:
    return (delivery.status, delivery.external_id, delivery.error)


def _finished(deliveries: list[Delivery]) -> bool:
    """True once at least one delivery exists and none is still waiting to be sent."""
    return bool(deliveries) and all(d.status is not DeliveryStatus.QUEUED for d in deliveries)


async def stream_delivery_events(
    message_id: UUID,
    *,
    deliveries: DeliveryRepository,
    poll_seconds: float = POLL_SECONDS,
    ping_seconds: float = PING_SECONDS,
    max_seconds: float = MAX_SECONDS,
    sleep: Sleep = asyncio.sleep,
) -> AsyncIterator[DeliveryEvent]:
    """Yield a snapshot, then every change, then `done` when nothing is left to send."""
    current = await deliveries.list_for_message(message_id)
    seen = {d.id: _fingerprint(d) for d in current}
    yield DeliveryEvent("snapshot", tuple(current))
    elapsed = 0.0
    quiet = 0.0
    while not _finished(current) and elapsed < max_seconds:
        await sleep(poll_seconds)
        elapsed += poll_seconds
        quiet += poll_seconds
        current = await deliveries.list_for_message(message_id)
        changed = [d for d in current if seen.get(d.id) != _fingerprint(d)]
        for delivery in changed:
            seen[delivery.id] = _fingerprint(delivery)
            yield DeliveryEvent("delivery", (delivery,))
            quiet = 0.0
        if quiet >= ping_seconds:
            quiet = 0.0
            yield DeliveryEvent("ping")
    yield DeliveryEvent("done")
