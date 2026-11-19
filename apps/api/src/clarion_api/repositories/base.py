from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from clarion_api.domain.models import Claim, SourcePassage

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
