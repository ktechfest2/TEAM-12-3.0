import math
from collections.abc import Sequence
from uuid import UUID

from clarion_api.domain.models import Claim, SourcePassage
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
