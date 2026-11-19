import math
from collections.abc import Sequence
from uuid import UUID

from clarion_api.domain.enums import ChannelKind, SubscriptionStatus
from clarion_api.domain.models import (
    AuditEvent,
    Claim,
    Delivery,
    MasterMessage,
    SmsSubscription,
    SourcePassage,
    Subscriber,
)
from clarion_api.repositories.base import MIN_SIMILARITY


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class MemorySourceRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, tuple[SourcePassage, list[float]]] = {}

    async def add(self, passage: SourcePassage, embedding: Sequence[float]) -> None:
        self._items[passage.id] = (passage, list(embedding))

    async def get(self, passage_id: UUID) -> SourcePassage | None:
        item = self._items.get(passage_id)
        return item[0] if item else None

    async def search(self, vector: Sequence[float], *, limit: int) -> list[SourcePassage]:
        scored = [(_cosine(vector, emb), p) for p, emb in self._items.values()]
        scored = [s for s in scored if s[0] >= MIN_SIMILARITY]
        scored.sort(key=lambda s: s[0], reverse=True)
        return [p for _, p in scored[:limit]]


class MemoryClaimRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Claim] = {}

    async def add(self, claim: Claim) -> None:
        self._items[claim.id] = claim

    async def get(self, claim_id: UUID) -> Claim | None:
        return self._items.get(claim_id)

    async def list_recent(self, *, limit: int) -> list[Claim]:
        return sorted(self._items.values(), key=lambda c: c.created_at, reverse=True)[:limit]


class MemoryMessageRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, MasterMessage] = {}

    async def save(self, message: MasterMessage) -> None:
        self._items[message.id] = message

    async def get(self, message_id: UUID) -> MasterMessage | None:
        return self._items.get(message_id)

    async def list_recent(self, *, limit: int) -> list[MasterMessage]:
        return sorted(self._items.values(), key=lambda m: m.created_at, reverse=True)[:limit]

    async def latest_integrity_hash(self, *, excluding: UUID | None = None) -> str | None:
        sealed = [
            m for m in self._items.values() if m.integrity_hash is not None and m.id != excluding
        ]
        if not sealed:
            return None
        return max(sealed, key=lambda m: m.created_at).integrity_hash


class MemoryDeliveryRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Delivery] = {}

    async def save(self, delivery: Delivery) -> None:
        self._items[delivery.id] = delivery

    async def get(self, delivery_id: UUID) -> Delivery | None:
        return self._items.get(delivery_id)

    async def list_for_message(self, message_id: UUID) -> list[Delivery]:
        found = [d for d in self._items.values() if d.message_id == message_id]
        return sorted(found, key=lambda d: d.created_at)

    async def list_recent(self, *, limit: int) -> list[Delivery]:
        return sorted(self._items.values(), key=lambda d: d.created_at, reverse=True)[:limit]


class MemorySubscriberRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[ChannelKind, str], Subscriber] = {}

    async def upsert(self, subscriber: Subscriber) -> Subscriber:
        key = (subscriber.channel, subscriber.address_hash)
        existing = self._items.get(key)
        if existing is not None:
            subscriber = existing.model_copy(
                update={"language": subscriber.language, "state": subscriber.state}
            )
        self._items[key] = subscriber
        return subscriber

    async def get(self, channel: ChannelKind, address_hash: str) -> Subscriber | None:
        return self._items.get((channel, address_hash))

    async def remove(self, channel: ChannelKind, address_hash: str) -> bool:
        return self._items.pop((channel, address_hash), None) is not None

    async def count(self) -> int:
        return len(self._items)


class MemorySmsSubscriptionRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, SmsSubscription] = {}

    async def save(self, subscription: SmsSubscription) -> None:
        self._items[subscription.id] = subscription

    async def get_by_hash(self, phone_hash: str) -> SmsSubscription | None:
        return next((s for s in self._items.values() if s.phone_hash == phone_hash), None)

    async def delete(self, subscription_id: UUID) -> bool:
        return self._items.pop(subscription_id, None) is not None

    async def list_active(self) -> list[SmsSubscription]:
        return [s for s in self._items.values() if s.status is SubscriptionStatus.ACTIVE]


class MemoryAuditRepository:
    def __init__(self) -> None:
        self._items: list[AuditEvent] = []

    async def add(self, event: AuditEvent) -> None:
        self._items.append(event)

    async def list_for_subject(
        self, subject_id: UUID, *, action: str | None = None
    ) -> list[AuditEvent]:
        return [
            e
            for e in self._items
            if e.subject_id == subject_id and (action is None or e.action == action)
        ]
