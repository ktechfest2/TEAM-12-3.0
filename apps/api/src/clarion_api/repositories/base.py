from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from clarion_api.domain.enums import ChannelKind
from clarion_api.domain.models import Claim, Delivery, MasterMessage, SourcePassage, Subscriber

# Passages less similar than this (cosine similarity) are never returned by search.
MIN_SIMILARITY = 0.15


class SourceRepository(Protocol):
    async def add(self, passage: SourcePassage, embedding: Sequence[float]) -> None: ...

    async def get(self, passage_id: UUID) -> SourcePassage | None: ...

    async def search(self, vector: Sequence[float], *, limit: int) -> list[SourcePassage]: ...


class ClaimRepository(Protocol):
    async def add(self, claim: Claim) -> None: ...

    async def get(self, claim_id: UUID) -> Claim | None: ...

    async def list_recent(self, *, limit: int) -> list[Claim]: ...


class MessageRepository(Protocol):
    async def save(self, message: MasterMessage) -> None:
        """Insert or replace the whole message: review and localisations included."""
        ...

    async def get(self, message_id: UUID) -> MasterMessage | None: ...

    async def list_recent(self, *, limit: int) -> list[MasterMessage]: ...

    async def latest_integrity_hash(self, *, excluding: UUID | None = None) -> str | None:
        """Hash of the most recently created sealed message, for chaining."""
        ...


class DeliveryRepository(Protocol):
    async def save(self, delivery: Delivery) -> None: ...

    async def get(self, delivery_id: UUID) -> Delivery | None: ...

    async def list_for_message(self, message_id: UUID) -> list[Delivery]: ...

    async def list_recent(self, *, limit: int) -> list[Delivery]: ...


class SubscriberRepository(Protocol):
    async def upsert(self, subscriber: Subscriber) -> Subscriber:
        """Insert, or update language and state of the existing subscriber with the same hash."""
        ...

    async def get(self, channel: ChannelKind, address_hash: str) -> Subscriber | None: ...

    async def remove(self, channel: ChannelKind, address_hash: str) -> bool:
        """Delete the subscriber. Returns False when there was none."""
        ...

    async def count(self) -> int: ...
