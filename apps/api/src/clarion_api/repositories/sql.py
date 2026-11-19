"""Postgres implementations of the repository protocols (SQLAlchemy async + pgvector).

Only this module maps database rows to domain models and back.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from clarion_api.db.tables import ClaimRow, SourcePassageRow
from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.domain.models import Claim, SourcePassage
from clarion_api.repositories.base import MIN_SIMILARITY

SessionFactory = async_sessionmaker[AsyncSession]


def _passage_from_row(row: SourcePassageRow) -> SourcePassage:
    return SourcePassage(
        id=row.id,
        created_at=row.created_at,
        document_title=row.document_title,
        publisher=row.publisher,
        url=row.url,
        published_on=row.published_on,
        text=row.text,
    )


def _claim_from_row(row: ClaimRow) -> Claim:
    return Claim(
        id=row.id,
        created_at=row.created_at,
        text=row.text,
        language=Language(row.language),
        submitted_via=ChannelKind(row.submitted_via),
        screenshot_key=row.screenshot_key,
    )


class SqlSourceRepository:
    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    async def add(self, passage: SourcePassage, embedding: Sequence[float]) -> None:
        row = SourcePassageRow(
            id=passage.id,
            created_at=passage.created_at,
            document_title=passage.document_title,
            publisher=passage.publisher,
            url=str(passage.url),
            published_on=passage.published_on,
            text=passage.text,
            embedding=list(embedding),
        )
        async with self._sessions.begin() as session:
            await session.merge(row)

    async def get(self, passage_id: UUID) -> SourcePassage | None:
        async with self._sessions() as session:
            row = await session.get(SourcePassageRow, passage_id)
            return _passage_from_row(row) if row else None

    async def search(self, vector: Sequence[float], *, limit: int) -> list[SourcePassage]:
        distance = SourcePassageRow.embedding.cosine_distance(list(vector))
        stmt = (
            select(SourcePassageRow)
            .where(distance <= 1.0 - MIN_SIMILARITY)
            .order_by(distance)
            .limit(limit)
        )
        async with self._sessions() as session:
            rows = (await session.scalars(stmt)).all()
            return [_passage_from_row(r) for r in rows]


class SqlClaimRepository:
    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    async def add(self, claim: Claim) -> None:
        row = ClaimRow(
            id=claim.id,
            created_at=claim.created_at,
            text=claim.text,
            language=claim.language.value,
            submitted_via=claim.submitted_via.value,
            screenshot_key=claim.screenshot_key,
        )
        async with self._sessions.begin() as session:
            await session.merge(row)

    async def get(self, claim_id: UUID) -> Claim | None:
        async with self._sessions() as session:
            row = await session.get(ClaimRow, claim_id)
            return _claim_from_row(row) if row else None

    async def list_recent(self, *, limit: int) -> list[Claim]:
        stmt = select(ClaimRow).order_by(ClaimRow.created_at.desc()).limit(limit)
        async with self._sessions() as session:
            return [_claim_from_row(r) for r in (await session.scalars(stmt)).all()]
