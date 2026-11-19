"""Postgres implementations of the repository protocols (SQLAlchemy async + pgvector).

Only this module maps database rows to domain models and back.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from clarion_api.db.tables import (
    ClaimRow,
    DeliveryRow,
    LocalisationRow,
    MessageRow,
    ReviewRow,
    SourcePassageRow,
    SubscriberRow,
)
from clarion_api.domain.enums import ChannelKind, DeliveryStatus, Language, ReviewStatus, Verdict
from clarion_api.domain.models import (
    Claim,
    Delivery,
    Localisation,
    MasterMessage,
    Review,
    SourcePassage,
    Subscriber,
)
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


def _review_from_row(row: ReviewRow, claim_id: UUID) -> Review:
    return Review(
        id=row.id,
        created_at=row.created_at,
        claim_id=claim_id,
        reviewer_id=row.reviewer_id,
        status=ReviewStatus(row.status),
        note=row.note,
    )


def _localisation_from_row(row: LocalisationRow) -> Localisation:
    return Localisation(
        id=row.id,
        created_at=row.created_at,
        language=Language(row.language),
        text=row.text,
        approved_by=row.approved_by,
    )


def _delivery_from_row(row: DeliveryRow) -> Delivery:
    return Delivery(
        id=row.id,
        created_at=row.created_at,
        message_id=row.message_id,
        channel=ChannelKind(row.channel),
        language=Language(row.language),
        status=DeliveryStatus(row.status),
        external_id=row.external_id,
        error=row.error,
        sent_at=row.sent_at,
    )


class SqlMessageRepository:
    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    async def save(self, message: MasterMessage) -> None:
        async with self._sessions.begin() as session:
            await session.merge(
                MessageRow(
                    id=message.id,
                    created_at=message.created_at,
                    claim_id=message.claim_id,
                    verdict=message.verdict.value,
                    passage_id=message.passage.id if message.passage else None,
                    summary=message.summary,
                    confidence=message.confidence,
                    integrity_hash=message.integrity_hash,
                )
            )
            if message.review is not None:
                await session.merge(
                    ReviewRow(
                        id=message.review.id,
                        created_at=message.review.created_at,
                        message_id=message.id,
                        reviewer_id=message.review.reviewer_id,
                        status=message.review.status.value,
                        note=message.review.note,
                    )
                )
            keep = [loc.id for loc in message.localisations]
            await session.execute(
                delete(LocalisationRow).where(
                    LocalisationRow.message_id == message.id, LocalisationRow.id.not_in(keep)
                )
            )
            for loc in message.localisations:
                await session.merge(
                    LocalisationRow(
                        id=loc.id,
                        created_at=loc.created_at,
                        message_id=message.id,
                        language=loc.language.value,
                        text=loc.text,
                        approved_by=loc.approved_by,
                    )
                )

    async def get(self, message_id: UUID) -> MasterMessage | None:
        async with self._sessions() as session:
            row = await session.get(MessageRow, message_id)
            return await self._load(session, row) if row else None

    async def list_recent(self, *, limit: int) -> list[MasterMessage]:
        stmt = select(MessageRow).order_by(MessageRow.created_at.desc()).limit(limit)
        async with self._sessions() as session:
            rows = (await session.scalars(stmt)).all()
            return [await self._load(session, r) for r in rows]

    async def latest_integrity_hash(self, *, excluding: UUID | None = None) -> str | None:
        stmt = (
            select(MessageRow.integrity_hash)
            .where(MessageRow.integrity_hash.is_not(None))
            .order_by(MessageRow.created_at.desc())
            .limit(1)
        )
        if excluding is not None:
            stmt = stmt.where(MessageRow.id != excluding)
        async with self._sessions() as session:
            return await session.scalar(stmt)

    @staticmethod
    async def _load(session: AsyncSession, row: MessageRow) -> MasterMessage:
        passage_row = (
            await session.get(SourcePassageRow, row.passage_id) if row.passage_id else None
        )
        review_row = await session.scalar(
            select(ReviewRow)
            .where(ReviewRow.message_id == row.id)
            .order_by(ReviewRow.created_at.desc())
            .limit(1)
        )
        loc_rows = (
            await session.scalars(
                select(LocalisationRow)
                .where(LocalisationRow.message_id == row.id)
                .order_by(LocalisationRow.created_at)
            )
        ).all()
        return MasterMessage(
            id=row.id,
            created_at=row.created_at,
            claim_id=row.claim_id,
            verdict=Verdict(row.verdict),
            passage=_passage_from_row(passage_row) if passage_row else None,
            summary=row.summary,
            confidence=row.confidence,
            review=_review_from_row(review_row, row.claim_id) if review_row else None,
            localisations=tuple(_localisation_from_row(r) for r in loc_rows),
            integrity_hash=row.integrity_hash,
        )


class SqlDeliveryRepository:
    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    async def save(self, delivery: Delivery) -> None:
        async with self._sessions.begin() as session:
            await session.merge(
                DeliveryRow(
                    id=delivery.id,
                    created_at=delivery.created_at,
                    message_id=delivery.message_id,
                    channel=delivery.channel.value,
                    language=delivery.language.value,
                    status=delivery.status.value,
                    external_id=delivery.external_id,
                    error=delivery.error,
                    sent_at=delivery.sent_at,
                )
            )

    async def get(self, delivery_id: UUID) -> Delivery | None:
        async with self._sessions() as session:
            row = await session.get(DeliveryRow, delivery_id)
            return _delivery_from_row(row) if row else None

    async def list_for_message(self, message_id: UUID) -> list[Delivery]:
        stmt = (
            select(DeliveryRow)
            .where(DeliveryRow.message_id == message_id)
            .order_by(DeliveryRow.created_at)
        )
        async with self._sessions() as session:
            return [_delivery_from_row(r) for r in (await session.scalars(stmt)).all()]

    async def list_recent(self, *, limit: int) -> list[Delivery]:
        stmt = select(DeliveryRow).order_by(DeliveryRow.created_at.desc()).limit(limit)
        async with self._sessions() as session:
            return [_delivery_from_row(r) for r in (await session.scalars(stmt)).all()]


def _subscriber_from_row(row: SubscriberRow) -> Subscriber:
    return Subscriber(
        id=row.id,
        created_at=row.created_at,
        channel=ChannelKind(row.channel),
        address_hash=row.address_hash,
        language=Language(row.language),
        state=row.state,
        consented_at=row.consented_at,
    )


class SqlSubscriberRepository:
    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    @staticmethod
    def _lookup(channel: ChannelKind, address_hash: str) -> Select[SubscriberRow]:
        return select(SubscriberRow).where(
            SubscriberRow.channel == channel.value, SubscriberRow.address_hash == address_hash
        )

    async def upsert(self, subscriber: Subscriber) -> Subscriber:
        async with self._sessions.begin() as session:
            row = await session.scalar(self._lookup(subscriber.channel, subscriber.address_hash))
            if row is None:
                row = SubscriberRow(
                    id=subscriber.id,
                    created_at=subscriber.created_at,
                    channel=subscriber.channel.value,
                    address_hash=subscriber.address_hash,
                    language=subscriber.language.value,
                    state=subscriber.state,
                    consented_at=subscriber.consented_at,
                )
                session.add(row)
            else:
                row.language = subscriber.language.value
                row.state = subscriber.state
            await session.flush()
            return _subscriber_from_row(row)

    async def get(self, channel: ChannelKind, address_hash: str) -> Subscriber | None:
        async with self._sessions() as session:
            row = await session.scalar(self._lookup(channel, address_hash))
            return _subscriber_from_row(row) if row else None

    async def remove(self, channel: ChannelKind, address_hash: str) -> bool:
        async with self._sessions.begin() as session:
            row = await session.scalar(self._lookup(channel, address_hash))
            if row is None:
                return False
            await session.delete(row)
            return True

    async def count(self) -> int:
        async with self._sessions() as session:
            return int(await session.scalar(select(func.count()).select_from(SubscriberRow)) or 0)
